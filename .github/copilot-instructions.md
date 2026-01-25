# Copilot Instructions for Stars Die Teaser Project (Clevertree)

This project is an animated teaser for "Stars Die" by Porcupine Tree, serving as a conceptual teaser for the game project **Forgotten Future**.

## Project Structure
- Each section of the song has its own folder (e.g., `00_intro`, `01_verse_1`, `08_outro`).
- Media, concept art, and section-specific notes should be kept within these folders.
- `Lyrics.md` contains the full lyrics with precise timestamps.
- `README.md` contains the master plan and refined timings.

## Animation Guidelines
- Most shots should be approximately one line of lyrics in length.
- The Nixon interlude starts at "Because of what you have done..." (original lines 26-29 are cut).
- Focus on atmospheric, realistic, and space-themed imagery consistent with the song's mood.

## Tooling
- Use `stable-ts` for precise lyric-to-audio alignment.
- Use `FFmpeg` for video/audio processing.
- Concept art is generated using Stable Diffusion or Midjourney.

## Coding & Automation
- When writing scripts (Python/Bash), prioritize automation for media organization and FFmpeg processing.
- Ensure any generated timestamps are formatted for easy import into animation software.

## Narrative Alignment
- **POV:** The story of **Forgotten Future** is told exclusively from Ren's POV. Maintain this perspective in any conceptual narrative elements.
- **Vessel Consciousness:** Vessels and Gorgons possess human-like or living consciousness. They are not mindless robots.

## Version Management
- **Source of Truth:** The current version is stored in `VERSION`.
- **Protocol:** Bump the version in `VERSION` on **every git commit**.
- **Reasonable Versioning:**
    - **Major (X.0.0):** Completion of a full song section (e.g., Intro, Verse 1 complete) or a total visual/stylistic overhaul.
    - **Minor (0.X.0):** New shot scripts, updated audio alignment, or significant tool automation improvements.
    - **Patch (0.0.X):** Precise timing tweaks, metadata corrections, or minor script bug fixes.

## Commit History
- **Requirement:** Maintain a `COMMIT_HISTORY.md` file in the root of the repository.
- **Protocol:** Update `COMMIT_HISTORY.md` with a one-line summary of the new commit on **every git commit**.
- **Syncing:** If you notice `COMMIT_HISTORY.md` is out of date, sync it immediately by running `git log --oneline > COMMIT_HISTORY.md`.

