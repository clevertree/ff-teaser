import os
import re
import json
import subprocess
from pathlib import Path

def get_video_duration(file_path):
    """Gets the duration of an audio/video file using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def parse_lyrics(lyrics_path):
    """Parses Lyrics.md into a list of (timestamp_seconds, text)."""
    with open(lyrics_path, 'r') as f:
        lines = f.readlines()
    
    lyrics = []
    # Match [MM:SS.hh] Text
    pattern = r"\[(\d{2}):(\d{2})\.(\d{2})\] (.*)"
    
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            m, s, h, text = match.groups()
            if "[CUT]" in text or "(Instrumental" in text or "(Final" in text:
                continue
            seconds = int(m) * 60 + int(s) + int(h) / 100
            lyrics.append((seconds, text.strip()))
    
    return lyrics

def create_srt(lyrics, output_path):
    """Creates an SRT subtitle file from parsed lyrics."""
    with open(output_path, 'w') as f:
        for i, (start, text) in enumerate(lyrics):
            # End time is the start of the next lyric, or start + 4 seconds
            end = lyrics[i+1][0] if i+1 < len(lyrics) else start + 4.0
            
            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds % 1) * 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"

            f.write(f"{i+1}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")

def assemble_video():
    base_dir = Path(__file__).parent
    audio_file = base_dir / "song.mp3"
    lyrics_file = base_dir / "Lyrics.md"
    srt_file = base_dir / "lyrics.srt"
    output_file = base_dir / "teaser_draft.mp4"
    
    if not audio_file.exists():
        print(f"Error: {audio_file} not found.")
        return

    # Parse lyrics and create SRT
    lyrics = parse_lyrics(lyrics_file)
    create_srt(lyrics, srt_file)

    # Define sections and their end times
    sections = [
        {"path": "00_intro", "end": 33.66},
        {"path": "01_verse_1", "end": 65.92},
        {"path": "02_chorus_1", "end": 100.22},
        {"path": "03_verse_2", "end": 132.08},
        {"path": "04_chorus_2", "end": 160.00},
        {"path": "05_interlude_nixon", "end": 203.27},
        {"path": "06_verse_3", "end": 250.44},
        {"path": "07_chorus_3", "end": 281.00},
        {"path": "08_outro", "end": 301.00}
    ]

    clips = []
    last_end = 0.0
    
    for section in sections:
        section_dir = base_dir / section["path"]
        
        # Look for images in [section]/[nn]_[description] folders
        # Prioritize images in the 'derive' subfolder if they exist
        hero_folders = sorted([d for d in section_dir.iterdir() if d.is_dir() and re.match(r"\d{2}_", d.name)])
        section_images = []
        
        for hf in hero_folders:
            derive_imgs = sorted(list(hf.glob("derive/hero_*_*.webp")))
            if derive_imgs:
                section_images.append(derive_imgs[0]) # Use the first derived variation
            else:
                base_imgs = sorted(list(hf.glob("hero_*_*.webp")))
                if base_imgs:
                    section_images.append(base_imgs[0])
        
        images = section_images
        
        if not images:
            last_end = section["end"]
            continue
            
        section_duration = section["end"] - last_end
        image_duration = section_duration / len(images)
        
        for i, img in enumerate(images):
            clips.append({
                "path": img,
                "duration": image_duration
            })
        
        last_end = section["end"]

    if not clips:
        print("No images found to assemble. Please run generate_hero_images.py first.")
        return

    # Build FFmpeg command with Ken Burns effect (slow zoom)
    filter_complex = ""
    inputs = []
    
    for i, clip in enumerate(clips):
        inputs.extend(["-loop", "1", "-t", str(clip["duration"]), "-i", str(clip["path"])])
        # Ken Burns: Zoom from 1.0 to 1.1 over the duration
        # Also scale and pad to 1920x1080
        filter_complex += (
            f"[{i}:v]scale=2000:-1,zoompan=z='min(zoom+0.0005,1.1)':d={int(clip['duration']*25)}:s=1920x1080:fps=25,"
            f"fade=t=in:st=0:d=0.5,fade=t=out:st={clip['duration']-0.5}:d=0.5[v{i}];"
        )
    
    concat_v = "".join([f"[v{i}]" for i in range(len(clips))])
    filter_complex += f"{concat_v}concat=n={len(clips)}:v=1:a=0[outv]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", str(audio_file),
        "-filter_complex", filter_complex + f",subtitles={srt_file.name}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=30'",
        "-map", "[outv]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_file)
    ]

    print("Assembling video with FFmpeg (this may take a few minutes)...")
    subprocess.run(cmd)
    print(f"Done! Video saved to {output_file}")

if __name__ == "__main__":
    assemble_video()
