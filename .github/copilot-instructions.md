# Copilot Instructions for Stars Die Teaser Project

This project is an animated teaser for "Stars Die" by Porcupine Tree, serving as a conceptual teaser for the game project **Forgotten Future**.

## Project Structure
- Each section of the song has its own folder (e.g., `00_intro`, `01_verse_1`, `08_outro`).
- Media, concept art, and section-specific notes should be kept within these folders.
- `Lyrics.md` contains the full lyrics with precise timestamps.
- `README.md` contains the master plan and refined timings.

## Animation Guidelines
- Most shots should be approximately one line of lyrics in length.
- The Nixon interlude starts at "Because of what you have done..." (original lines 26-29 are cut).
- Focus on atmospheric, psychedelic, and space-themed imagery consistent with the song's mood.

## Tooling
- Use `stable-ts` for precise lyric-to-audio alignment.
- Use `FFmpeg` for video/audio processing.
- Concept art is generated using Stable Diffusion or Midjourney.

## Coding & Automation
- When writing scripts (Python/Bash), prioritize automation for media organization and FFmpeg processing.
- Ensure any generated timestamps are formatted for easy import into animation software.
