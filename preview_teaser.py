import subprocess
from pathlib import Path
from assemble_teaser import assemble_video

if __name__ == "__main__":
    print("Generating a preview of the teaser with currently available images...")
    assemble_video()
    print("\nPreview generated as 'teaser_draft.mp4'.")
    print("Note: This will only include sections that have images generated.")
