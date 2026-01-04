import os
import re
import time
import requests
import hashlib
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configuration
# PROVIDER = "pollinations"
# MODEL = "flux" # Options: flux, flux-realism, flux-civitai, flux-anime, flux-3d, any-dark, flux-pro

PROVIDER = "openai"
MODEL = "dall-e-3" # Options: dall-e-3, dall-e-2

# Known placeholder/error images from Pollinations.ai
KNOWN_BAD_HASHES = [
    "cd399a37a8546090283d28b638b3191f", # "Rate Limit Reached" placeholder
    "2090a5dc21c32952cbf8496339752bd1", # Another "Rate Limit Reached" variant
]

def parse_prompts(file_path):
    """Parses the prompts.md file to extract hero image titles and prompts."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract the style guide
    style_match = re.search(r"\*\*Style Guide:\*\* (.*)", content)
    style_guide = style_match.group(1) if style_match else ""
    
    # Extract hero images
    # Matches "## Hero Image X: Title" and the following "**Prompt:** Prompt text"
    pattern = r"## Hero Image \d+: (.*?)\n\*\*Prompt:\*\* (.*?)(?=\n##|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    prompts = []
    for title, prompt in matches:
        full_prompt = f"{style_guide} {prompt.strip()}"
        prompts.append({
            "title": title.strip().replace(" ", "_").lower(),
            "prompt": full_prompt
        })
    
    return prompts

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
        with open(output_path, 'wb') as handler:
            handler.write(img_data)
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
            
            with open(output_path, 'wb') as handler:
                handler.write(content)
            print(f"Successfully saved to {output_path}")
            return True
        else:
            print(f"Error: Pollinations.ai returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error generating image with Pollinations: {e}")
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
            output_file = section / f"hero_{i+1}_{p['title']}.png"
            
            if output_file.exists():
                # Check if existing file is a bad placeholder
                with open(output_file, 'rb') as f:
                    existing_content = f.read()
                    existing_hash = hashlib.md5(existing_content).hexdigest()
                
                if existing_hash in KNOWN_BAD_HASHES:
                    print(f"Found bad placeholder at {output_file.name}, will re-generate.")
                    output_file.unlink()
                else:
                    print(f"Skipping {output_file.name}, already exists and looks valid.")
                    continue
            
            if PROVIDER == "openai":
                success = generate_image_openai(p['prompt'], output_file)
            else:
                success = generate_image_pollinations(p['prompt'], output_file)
                
            if success:
                # Small delay to be polite
                time.sleep(2)
            else:
                print(f"Failed to generate {output_file.name}. Moving to next...")

if __name__ == "__main__":
    main()
