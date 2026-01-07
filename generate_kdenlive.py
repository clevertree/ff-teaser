import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

def parse_lyrics(lyrics_path):
    """Parses Lyrics.md into a list of (timestamp_seconds, text)."""
    if not os.path.exists(lyrics_path):
        return []
    with open(lyrics_path, 'r') as f:
        lines = f.readlines()
    
    lyrics = []
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

def generate_kdenlive():
    base_dir = Path(__file__).parent.absolute()
    audio_file = "song.mp3"
    lyrics_file = "Lyrics.md"
    srt_file = "lyrics.srt"
    output_kdenlive = base_dir / "teaser.kdenlive"
    
    # Parse lyrics and create SRT
    lyrics = parse_lyrics(base_dir / lyrics_file)
    create_srt(lyrics, base_dir / srt_file)

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

    fps = 25
    clips = []
    last_end = 0.0
    
    for section in sections:
        section_dir = base_dir / section["path"]
        if not section_dir.exists():
            last_end = section["end"]
            continue

        hero_folders = sorted([d for d in section_dir.iterdir() if d.is_dir() and re.match(r"\d{2}_", d.name)])
        section_images = []
        
        for hf in hero_folders:
            derive_imgs = sorted(list(hf.glob("derive/hero_*_*.webp")))
            if derive_imgs:
                section_images.append(derive_imgs[0])
            else:
                base_imgs = sorted(list(hf.glob("hero_*_*.webp")))
                if base_imgs:
                    section_images.append(base_imgs[0])
        
        if not section_images:
            last_end = section["end"]
            continue
            
        section_duration = section["end"] - last_end
        image_duration = section_duration / len(section_images)
        
        for img in section_images:
            clips.append({
                "path": img.relative_to(base_dir),
                "duration": image_duration
            })
        
        last_end = section["end"]

    if not clips:
        print("No images found to assemble.")
        return

    # Create MLT XML
    mlt = ET.Element("mlt", {
        "LC_NUMERIC": "C",
        "version": "7.22.0",
        "root": str(base_dir)
    })
    
    profile = ET.SubElement(mlt, "profile", {
        "description": "HD 1080p 25fps",
        "frame_rate_num": str(fps),
        "frame_rate_den": "1",
        "width": "1920",
        "height": "1080",
        "progressive": "1",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "colorspace": "709"
    })

    # Audio Producer
    audio_producer = ET.SubElement(mlt, "producer", {"id": "audio_song"})
    ET.SubElement(audio_producer, "property", {"name": "resource"}).text = audio_file
    
    # Image Producers
    for i, clip in enumerate(clips):
        duration_frames = int(clip["duration"] * fps)
        pid = f"producer_{i}"
        
        p = ET.SubElement(mlt, "producer", {"id": pid, "in": "0", "out": str(duration_frames - 1)})
        ET.SubElement(p, "property", {"name": "resource"}).text = str(clip["path"])
        ET.SubElement(p, "property", {"name": "ttl"}).text = "1"
        ET.SubElement(p, "property", {"name": "aspect_ratio"}).text = "1"
        
        # Ken Burns Filter (Affine)
        f_affine = ET.SubElement(p, "filter", {"id": f"filter_affine_{i}"})
        ET.SubElement(f_affine, "property", {"name": "mlt_service"}).text = "affine"
        ET.SubElement(f_affine, "property", {"name": "rect"}).text = f"0=0 0 1920 1080 100; {duration_frames-1}=-96 -54 2112 1188 100"
        
        # Fade In/Out Filters
        f_in = ET.SubElement(p, "filter", {"id": f"filter_in_{i}"})
        ET.SubElement(f_in, "property", {"name": "mlt_service"}).text = "brightness"
        ET.SubElement(f_in, "property", {"name": "level"}).text = "0=0; 12=1.0"
        
        f_out = ET.SubElement(p, "filter", {"id": f"filter_out_{i}"})
        ET.SubElement(f_out, "property", {"name": "mlt_service"}).text = "brightness"
        ET.SubElement(f_out, "property", {"name": "level"}).text = f"{duration_frames-13}=1.0; {duration_frames-1}=0"

    # Playlist
    playlist = ET.SubElement(mlt, "playlist", {"id": "main_bin"})
    total_frames = 0
    for i, clip in enumerate(clips):
        duration_frames = int(clip["duration"] * fps)
        pid = f"producer_{i}"
        ET.SubElement(playlist, "entry", {"producer": pid, "in": "0", "out": str(duration_frames - 1)})
        total_frames += duration_frames

    # Tractor for combining everything
    tractor = ET.SubElement(mlt, "tractor", {"id": "tractor0", "in": "0", "out": str(total_frames - 1)})
    multitrack = ET.SubElement(tractor, "multitrack")
    ET.SubElement(multitrack, "track", {"producer": "main_bin"})
    ET.SubElement(multitrack, "track", {"producer": "audio_song"})
    
    # Subtitles filter on the tractor
    f_sub = ET.SubElement(tractor, "filter")
    ET.SubElement(f_sub, "property", {"name": "mlt_service"}).text = "avfilter.subtitles"
    ET.SubElement(f_sub, "property", {"name": "av.filename"}).text = str(srt_file)
    ET.SubElement(f_sub, "property", {"name": "av.force_style"}).text = "FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=30"

    # Serialize and save
    xml_str = ET.tostring(mlt, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    with open(output_kdenlive, "w") as f:
        f.write(pretty_xml)
        
    print(f"Kdenlive project generated: {output_kdenlive}")

if __name__ == "__main__":
    generate_kdenlive()
