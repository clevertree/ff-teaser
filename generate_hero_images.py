import os
import re
import time
import requests
import hashlib
import base64
import io
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Configuration
# PROVIDER = "pollinations"
# MODEL = "flux" # Options: flux, flux-realism, flux-civitai, flux-anime, flux-3d, any-dark, flux-pro

PROVIDER = "openai"
MODEL = "dall-e-3" # Options: dall-e-3, dall-e-2

# Local Stable Diffusion Configuration
SD_URL = os.getenv("STABLE_DIFFUSION_URL", "http://127.0.0.1:7860")

# Known placeholder/error images from Pollinations.ai
KNOWN_BAD_HASHES = [
    "cd399a37a8546090283d28b638b3191f", # "Rate Limit Reached" placeholder
    "2090a5dc21c32952cbf8496339752bd1", # Another "Rate Limit Reached" variant
]

def parse_prompts(file_path):
    """Parses the prompts.md file to extract titles and prompts."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract the style guide
    style_match = re.search(r"\*\*Style Guide:\*\* (.*)", content)
    style_guide = style_match.group(1) if style_match else ""
    
    # Split by any ## header sections
    sections = re.split(r"## ", content)
    
    prompts = []
    # Skip the first part before the first ## if it's there
    for section in sections[1:]:
        lines = section.split('\n', 1)
        if not lines:
            continue
            
        header = lines[0].strip()
        # Remove "Hero Image N: " if it exists to get a clean title
        title = re.sub(r"Hero Image \d+: ", "", header).strip()
        
        section_content = lines[1] if len(lines) > 1 else ""
        
        # Extract prompt and optional reference
        prompt_match = re.search(r"\*\*Prompt:\*\* (.*?)(?=\n\*\*Reference:\*\*|\Z)", section_content, re.DOTALL)
        ref_match = re.search(r"\*\*Reference:\*\* (.*?)(?=\n|$)", section_content)
        
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            full_prompt = f"{style_guide} {prompt_text}"
            
            prompt_data = {
                "title": title.replace(" ", "_").lower(),
                "prompt": full_prompt
            }
            if ref_match:
                prompt_data["reference"] = ref_match.group(1).strip()
            
            prompts.append(prompt_data)
    
    return prompts

def generate_variation_openai(reference_path, output_path):
    """Generates a variation of an existing image using OpenAI (DALL-E 2)."""
    print(f"Generating variation of {reference_path} for {output_path.name}...")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Variations require a PNG file under 4MB, square.
        # We'll use PIL to ensure it's a PNG and square.
        with Image.open(reference_path) as img:
            # Convert to RGBA if necessary
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            # Ensure it's square (crop if necessary)
            width, height = img.size
            if width != height:
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2
                img = img.crop((left, top, right, bottom))
            
            # Save to a bytes buffer as PNG
            byte_stream = io.BytesIO()
            img.save(byte_stream, format="PNG")
            byte_array = byte_stream.getvalue()
            
        response = client.images.create_variation(
            image=byte_array,
            n=1,
            size="1024x1024",
            model="dall-e-2"
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        
        # Convert to WebP
        with Image.open(io.BytesIO(img_data)) as img:
            img.save(output_path, "WEBP")
            
        print(f"Successfully saved variation to {output_path}")
        return True
    except Exception as e:
        print(f"Error generating variation with OpenAI: {e}")
        return False

def generate_image_openai(prompt, output_path):
    """Generates an image using OpenAI's DALL-E API."""
    print(f"Generating image with OpenAI ({MODEL}) for: {output_path.name}...")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model=MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        
        # Convert to WebP
        with Image.open(io.BytesIO(img_data)) as img:
            img.save(output_path, "WEBP")
            
        print(f"Successfully saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error generating image with OpenAI: {e}")
        return False

def generate_image_pollinations(prompt, output_path):
    """Generates an image using Pollinations.ai (Free, no API key required)."""
    print(f"Generating image with Pollinations ({MODEL}) for: {output_path.name}...")
    try:
        # Encode the prompt for the URL
        encoded_prompt = quote(prompt)
        # Pollinations.ai URL format with model selection
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={int(time.time())}&model={MODEL}"
        print(f"Requesting: {image_url}")
        
        response = requests.get(image_url, timeout=65)
        if response.status_code == 200:
            content = response.content
            
            # Validate image content
            content_hash = hashlib.md5(content).hexdigest()
            if content_hash in KNOWN_BAD_HASHES:
                print(f"CRITICAL: Detected rate-limit placeholder image (hash: {content_hash}). Exiting.")
                exit(1)
            
            # AI generated 1024x1024 images are typically > 200KB. 
            # The rate limit image is ~76KB - 95KB.
            if len(content) < 100000:
                print(f"Warning: Image size is unusually small ({len(content)} bytes). Hash: {content_hash}")
            
            # Convert to WebP
            with Image.open(io.BytesIO(content)) as img:
                img.save(output_path, "WEBP")
            print(f"Successfully saved to {output_path}")
            return True
        else:
            print(f"Error: Pollinations.ai returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error generating image with Pollinations: {e}")
        return False

def generate_image_sd_local(prompt, output_path, reference_path=None):
    """Generates an image using a local Stable Diffusion API (Automatic1111)."""
    print(f"Generating image with Local SD for: {output_path.name}...")
    
    payload = {
        "prompt": prompt,
        "steps": 30,
        "width": 1024,
        "height": 1024,
        "cfg_scale": 7,
    }
    
    endpoint = f"{SD_URL}/sdapi/v1/txt2img"
    
    if reference_path:
        with open(reference_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        payload["init_images"] = [img_base64]
        payload["denoising_strength"] = 0.55 # Balanced between original and new prompt
        endpoint = f"{SD_URL}/sdapi/v1/img2img"

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
        r = response.json()
        
        # SD API returns a list of images in base64
        image_data = base64.b64decode(r['images'][0])
        
        # Convert to WebP
        with Image.open(io.BytesIO(image_data)) as img:
            img.save(output_path, "WEBP")
            
        print(f"Successfully saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error generating image with Local SD: {e}")
        return False

def main():
    base_dir = Path(__file__).parent
    sections = sorted([d for d in base_dir.iterdir() if d.is_dir() and re.match(r"\d{2}_", d.name)])
    
    for section in sections:
        prompt_file = section / "prompts.md"
        if not prompt_file.exists():
            continue
        
        print(f"\nProcessing section: {section.name}")
        prompts = parse_prompts(prompt_file)
        
        for i, p in enumerate(prompts):
            # New structure: [section]/[nn]_[title]/hero_[n]_[title].webp
            hero_dir = section / f"{str(i+1).zfill(2)}_{p['title']}"
            hero_dir.mkdir(exist_ok=True)
            output_file = hero_dir / f"hero_{i+1}_{p['title']}.webp"
            
            if output_file.exists():
                # Check if existing file is a bad placeholder
                with open(output_file, 'rb') as f:
                    existing_content = f.read()
                    existing_hash = hashlib.md5(existing_content).hexdigest()
                
                if existing_hash in KNOWN_BAD_HASHES:
                    print(f"Found bad placeholder at {output_file.name}, will re-generate.")
                    output_file.unlink()
                else:
                    print(f"Base image {output_file.name} exists and is valid.")
                    
                    # Check for derived image
                    derive_dir = hero_dir / "derive"
                    derive_file = derive_dir / output_file.name
                    
                    if derive_file.exists():
                        print(f"Skipping derived image {derive_file.name}, already exists.")
                        continue
                        
                    print(f"Generating derived variation in {derive_dir.name}/...")
                    derive_dir.mkdir(exist_ok=True)
                    
                    success = False
                    if PROVIDER == "openai":
                        success = generate_variation_openai(output_file, derive_file)
                    elif PROVIDER == "stable-diffusion":
                        success = generate_image_sd_local(p['prompt'], derive_file, output_file)
                    else:
                        print(f"Variations not supported for {PROVIDER}. Skipping derive.")
                    
                    if success:
                        time.sleep(2)
                    continue
            
            success = False
            if "reference" in p:
                ref_path = base_dir / p["reference"]
                if not ref_path.exists():
                    ref_path = section / p["reference"]
                
                if ref_path.exists():
                    if PROVIDER == "openai":
                        success = generate_variation_openai(ref_path, output_file)
                    elif PROVIDER == "stable-diffusion":
                        success = generate_image_sd_local(p['prompt'], output_file, ref_path)
                    else:
                        print(f"Reference image found but img2img not implemented for {PROVIDER}. Using text-to-image.")
                        success = generate_image_pollinations(p['prompt'], output_file)
                else:
                    print(f"Reference image {p['reference']} not found. Using text-to-image.")
                    if PROVIDER == "openai":
                        success = generate_image_openai(p['prompt'], output_file)
                    elif PROVIDER == "stable-diffusion":
                        success = generate_image_sd_local(p['prompt'], output_file)
                    else:
                        success = generate_image_pollinations(p['prompt'], output_file)
            else:
                if PROVIDER == "openai":
                    success = generate_image_openai(p['prompt'], output_file)
                elif PROVIDER == "stable-diffusion":
                    success = generate_image_sd_local(p['prompt'], output_file)
                else:
                    success = generate_image_pollinations(p['prompt'], output_file)
                
            if success:
                # Small delay to be polite
                time.sleep(2)
            else:
                print(f"Failed to generate {output_file.name}. Moving to next...")

if __name__ == "__main__":
    main()
