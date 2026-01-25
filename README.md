![img.png](img.png)![img_1.png](img_1.png)# Stars Die - Animated Teaser Plan

A Clevertree Production.

This project is an animated teaser for the song **Stars Die** by Porcupine Tree, serving as a conceptual teaser for the **Forgotten Future** narrative.

## Story Context

**Forgotten Future** is an AI-driven science fiction novel set in a post-apocalyptic Earth, ~15 years after the "Cataclysm"—the shattering of the Moon and the arrival of colossal mechanical entities. The narrative follows **Ren**, a humanoid Wood Vessel whose body and memory were reset to infancy at **Cradle Zero** before being raised in suburban anonymity.

The teaser's imagery and tone directly parallel the events depicted in the story:
- **The Moon's destruction** (opening verses) mirrors the Lunar Capacitor discharge and the resulting **Great Fry**.
- **The Monoliths' arrival** (verse 1) depicts the First Wave of massive, lumbering entities during the **Decade of Revelation**. These stadium-sized industrial machines feature **two massive legs and two primary arms**—forming a four-pointed stance often mistaken for a tripod by the public. They are grown organic-mechanical hybrids, distinct from the smaller, Wellsian **Striders** built by the **Gorgons** in the After Time.
- **Humanity's dependency** (verses 2-3) reflects the aftermath where the **Archivists** (rebranded Technocratic Core) offer a utopian paradise of "no want and no pain" to erase indigenous culture and establish total control.

**Narrative Status:** Part 1 of the manuscript is complete. See [ff-story/chapters/INDEX.md](../ff-story/chapters/INDEX.md) for progress (16 chapters complete: "Awakening" to "The Cascade").

## Key Visual Motifs
- **Cradle Zero:** The original terrestrial base, now a "Fire City" with a massive **Pillar of Fire** stretching into the sky. It is guarded by **The Great Beast**, a dormant Elder Monolith.
- **Cradle Prime:** The primary enemy lunar base and first contact site.
- **Cradle Prime:** The shielded **Lunar Pyramid**, now the headquarters of the Archivists.
- **Synodic Aesthetic:** 
    - **Monoliths:** Stadium-sized, grown organic-mechanical industrial plants with two legs, two arms, and a forward-arching head. Mistakenly called "Tripods" due to their movement patterns.
    - **Striders:** Smaller, high-speed vehicles piloted by **Gorgons**. Closely resemble Wellsian "Tripods" (articulated hoods, thin legs, tentacles). These fire **invisible heat rays** and were engineered by the Core as "perfect slave" builders.
- **The Vessels:** 
    - **Ren:** Adolescent protagonist carrying **AI Lynn** as a spectral data-stream in his Aether-Drive.
    - **Rahu & Tor:** Reset loyalist commanders in clinical, Synodic-grown armor.
    - **Metal Vessels:** Numerous, shared-consciousness units lacking individual spirits.
    - **Gorgons (Builders):** Fire-aligned metallic entities with shared hiveminds. Evolved as a static Core experiment on the Moon; they migrate to Fire Cities like **Cradle Zero** for warmth.

## Song Structure & Refined Timings

*Timings updated based on `stable-ts` analysis of `song.mp3`.*

### [00_intro](00_intro) (0:00 - 0:33)
- Atmospheric space sounds and instrumental buildup.

### [01_verse_1](01_verse_1) (0:33 - 1:05)
- The moon shook (0:33 - 0:35)
- And curled up like gentle fire (0:35 - 0:42)
- The ocean glazed (0:42 - 0:46)
- And melted wire (0:46 - 0:53)
- Voices buzzed in spiral eyes (0:56 - 1:00)
- Stars dived in blinding skies (1:00 - 1:05)

### [02_chorus_1](02_chorus_1) (1:05 - 1:40)
- Stars die (1:05 - 1:12)
- Blinding skies (1:20 - 1:24)
- Instrumental transition (1:24 - 1:40)

### [03_verse_2](03_verse_2) (1:40 - 2:12)
- Tree cracked (1:40 - 1:41)
- And mountain cried (1:43 - 1:48)
- Bridges broke (1:51 - 1:52)
- And window sighed (1:57 - 2:00)
- Cells grew up and rivers burst (2:02 - 2:06)
- Sound obscured and sense reversed (2:07 - 2:11)

### [04_chorus_2](04_chorus_2) (2:12 - 2:40)
- Stars die (2:12 - 2:16)
- Blinding skies (2:26 - 2:30)
- Transition to Nixon Interlude (2:30 - 2:40)

### [05_interlude_nixon](05_interlude_nixon) (2:40 - 3:23)
- Nixon speech starts at "Because of what you have done..." (2:40)
- Atmospheric soundscapes behind the speech.
- Fades to black by 3:23.

### [06_verse_3](06_verse_3) (3:23 - 4:10)
- **3:23:** Music kicks in. Fast cuts of **Synodic Reconstruction** and the **Archivist Vanguard**.
- Idle mind (3:35 - 3:42)
- And severed soul (3:42 - 3:47)
- Silent nerves (3:47 - 3:52)
- And begging bowl (3:52 - 3:57)
- Shallow haze to blast a way (3:57 - 4:03)
- Hyper sleep to end the day (4:03 - 4:10)

### [07_chorus_3](07_chorus_3) (4:10 - 4:41)
- Stars die (4:10 - 4:20)
- Blinding skies (4:20 - 4:41)

### [08_outro](08_outro) (4:41 - 5:01)
- **4:41:** Music kicks back in. Final conflict sequence: The **Reclamation of Cradle Zero**, Metal Vessel phalanxes, and the ascent of the **Archivists**.
- Final serene shot of Moon fragments and title card.

---

## Recommended Tools & Solutions

### Audio-to-Text & Alignment
- **[OpenAI Whisper](https://github.com/openai/whisper):** For high-accuracy transcription.
- **[stable-ts](https://github.com/jianfch/stable-ts):** A modification of Whisper that provides word-level timestamps, ideal for syncing lyrics to animation.
- **[Aeneas](https://github.com/readbeyond/aeneas):** A tool for automatically generating synchronization between text and audio.

### Concept Art Generation
- **[Stable Diffusion (Local)](https://github.com/AUTOMATIC1111/stable-diffusion-webui):** Use ComfyUI or Automatic1111 for full control over style and consistency.
- **[Midjourney](https://www.midjourney.com/):** Excellent for high-fidelity artistic concepts.
- **[Krea.ai](https://www.krea.ai/):** Great for real-time enhancement and upscaling of generated art.
- **[Adobe Firefly](https://www.adobe.com/products/firefly.html):** Good for integrated workflows if using After Effects.

### Animation & Video Editing
- **[Blender](https://www.blender.org/):** For 3D scenes and grease pencil animations.
- **[FFmpeg](https://ffmpeg.org/):** Essential CLI tool for batch processing video, audio, and image sequences.
- **[DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve):** For final color grading and assembly.

## Workflow
1.  **Setup Environment:**
    ```bash
    # Activate the virtual environment
    source .venv/bin/activate
    ```
2.  **Refine Timings:** Use `stable-ts` to get exact timestamps for each line.
    ```bash
    # Example usage
    stable-ts audio.mp3 -o lyrics.json
    ```
3.  **Concept Art:** Generate 3-5 keyframes per section in the respective folders.
4.  **Storyboarding:** Use the folders to organize sketches and reference images.
5.  **Production:** Build scenes based on the concept art and timings.
# ff-teaser
