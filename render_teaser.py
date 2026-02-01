import subprocess
import os
from pathlib import Path

def render():
    base_dir = Path(__file__).parent.absolute()
    input_file = base_dir / "teaser.kdenlive"
    output_file = base_dir / "teaser_final.mp4"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found. Please run 'python3 generate_kdenlive.py' first.")
        return

    print(f"Lemdering {input_file.name} to {output_file.name} using melt...")
    
    # We use melt to render the MLT XML (Kdenlive) file.
    # The consumer 'avformat' is used for encoding to MP4.
    cmd = [
        "melt", str(input_file),
        "-consumer", f"avformat:{str(output_file)}",
        "vcodec=libx264",
        "acodec=aac",
        "pix_fmt=yuv420p",
        "preset=medium",
        "crf=23",
        "real_time=-1" # Disable real-time to ensure all frames are processed
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccessfully rendered teaser to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"\nError during rendering: {e}")
    except FileNotFoundError:
        print("\nError: 'melt' command not found. Please ensure MLT is installed.")

if __name__ == "__main__":
    render()
