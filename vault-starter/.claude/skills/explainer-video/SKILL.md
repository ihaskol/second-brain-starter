---
name: explainer-video
description: Make a narrated, captioned explainer video or animation from an approved script, drawn in code (no image generator). Two styles: a 16:9 whiteboard (hand-drawn doodles that draw themselves) and a 9:16 colored-pencil "crayon" short for phones, plus an interactive in-page animation player. Includes local text-to-speech (Kokoro), music mixing under the voice, frame recording and MP4 encoding. Use when the user asks for an explainer video, a whiteboard or doodle video, an animated walkthrough of a process, a short vertical video, or a narrated animation for a deck or a web page.
argument-hint: '<topic or script file> [--style whiteboard|crayon|player] [--length 60s|6min]'
disable-model-invocation: false
---

# Explainer Video

## Purpose

Turn verified content into a short animated video, drawn entirely in code: rough.js doodles on an SVG board, revealed in step with a synthetic narrator, over quiet music, with captions. The board is deterministic (`render(t)` draws the exact frame for time `t`), so every frame can be recorded, re-rendered after a one-word fix, or played interactively in a web page.

It cannot make photoreal, 3D, claymation or detailed illustrated styles; those need a generative video tool. For those, write a scene-by-scene storyboard with one prompt per scene for the user's own tool, then add voice, captions and the edit with the scripts here.

## Rules (read first)

- **The script is the source of truth.** Every fact on the board and in the voice comes from an approved script whose claims are checked against sources (`RESEARCH_PROTOCOL.md`). Keep a "claim → where it is stated" table at the end of the script.
- **Get the script approved before rendering.** Show a sample scene first (5–15 s) to agree the style, then build the rest.
- **Invented examples are labelled**: "Imagine…", "an invented example", or "(scores invented for this example)" on screen and in the notes. Never present an illustration as a result.
- **No real people, brands or organisations imitated.** A style taken from someone's video is fine; their characters, logos and brand are not.
- **Voice:** synthetic (Kokoro, local). Say so in the credits. **Music:** only a track whose licence you checked (CC0 recommended); record its source in a `SOURCE.md` next to it. Never upload anywhere unless the user asks.
- **Accessibility:** captions always, either a WebVTT sidecar or burned in for slides and social video. Keep music ≥ 20 dB under speech (WCAG 1.4.7); `mix.py` holds it at 26 dB.
- One idea per scene, in plain words. Short vertical videos use one sentence per scene, 4–6 s each.

## Pick the style

| Style | File | Shape | Best for |
|---|---|---|---|
| **Whiteboard** | `assets/whiteboard.html` | 16:9, 1920×1080 | Explaining a system or argument (2–6 min); hubs and decks |
| **Crayon** | `assets/crayon.html` | 9:16, 1080×1920 | A story told in ~45–60 s on a phone: pastel pencil fill, paper grain, a big time label ("MONDAY"), typed captions, pop-in speech bubbles |
| **Interactive player** | `assets/player.js` | any | Embedding in a page: Play/Pause, chapter buttons, slider, live captions, transcript, optional narration synced to the clock |

## Pipeline

1. **Script.** Write `script.json` (format in `scripts/narrate.py`): scenes, with one or more lines each, and for crayon a `label` per scene. Spoken-only replacements go in `"say"` (e.g. `"0.98": "zero point nine eight"`), so captions keep the digits.
2. **Copy the assets.** Copy `assets/` into the project, e.g. `_build/_video/`. The engine pages load `vendor/rough.js` and `fonts/PatrickHand-Regular.ttf` by relative path.
3. **Narrate:** `python scripts/narrate.py script.json out --kokoro <model dir>`. This writes `voice.wav`, `timing.json` (scene starts and each line's time and duration) and `captions.vtt`. The timing drives the drawing, so words appear as they are spoken.
4. **Draw the scenes.**
   - **Whiteboard:** one `BUILD.push(()=>{…})` per scene. `P(j,"phrase")` gives the moment segment `j` says that phrase. Use `title()`, `text()` and `doodle()` with the `D` library: robot, person, doc, folder, cabinet, arrow, magnifier, bars, tick, cross, stop, clock, scale, padlock, key.
   - **Crayon:** one `SCENE[i]=s=>{…}` per scene. Use `person()`, `robot()`, `bubble()` and `sparkle()` with the kinds `draw`, `type`, `fade`, `pop`, `drift` and `mv` (a drawing that moves along keyframes).
   - Keep the layout inside the safe area. Crayon content goes above the ground line (y 1150); the label and caption go below it.
5. **Look before recording:** `STILLS=5,12,30 node scripts/record.js page.html out/timing.json out/st`. Check every scene's last frame for overlaps, then fix and look again. Most bugs show here: text missing, labels on top of arrows, pale text colours.
6. **Record:** `node scripts/record.js page.html out/timing.json frames [fps] [w] [h]`. Use 25 fps for whiteboard and 30 for crayon (1080 1920). Set `PWC` to a local `playwright-core`.
7. **Mix:** `python scripts/mix.py out/voice.wav music.wav mix.m4a <total>`. It applies a voice EQ, filters the music out of the speech band, keeps the music 26 dB under speech and slightly up in pauses, and normalises to −16 LUFS.
8. **Encode:** `scripts/make_mp4.sh frames <fps> mix.m4a out.mp4 [cover.jpg]`. Use a cover when the video goes on a slide, because Keynote and PowerPoint show the first frame. Shift caption times by the cover length.
9. **Deliver.**
   - Full-resolution MP4 plus `.vtt`.
   - For a web page, a 540p or 720p copy. On the artifact host it must be fetched as a Blob to seek; the host refuses `.vtt` and `.m4a`. See `web-artifact-workflow`, "Media and files on the artifact host".
   - For a deck, embed with python-pptx `add_movie(…, poster_frame_image=…, mime_type="video/mp4")` and put the timed script in the notes. Check that Keynote imports it.
10. **Record** the build in the project's `PROJECT-STATE.md`: files, script version, voice, music source and QA.

## Interactive player (no video file)

Run the whiteboard engine, serialise the drawn SVG and the timeline, then mount it with `wfMount(root, WF, {audio, fetchAudio})`. It draws from data and needs no rough.js at runtime. With `audio`, the clock follows the narration and chapter jumps stay in sync. A single-file page can embed the font and audio as `data:` URIs and works offline. The same page in a `?record` mode can be recorded to MP4, with captions in a strip under the board.

## Setup (once per machine)

- **Python 3.11 venv:** `pip install kokoro-onnx soundfile numpy espeakng-loader`. Download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from the kokoro-onnx GitHub releases. Voice `af_heart` at speed 1.05 reads clearly.
- **Tools:** `ffmpeg`, plus Node with `playwright-core` and a Chromium (`npx playwright install chromium`).
- **Music:** pick a CC0 track with no lyrics or drums, and soft piano or pads. Save it with a `SOURCE.md` (title, author, URL, licence, date checked).

## Pitfalls learned

- espeak-ng fails on paths with spaces. `narrate.py` copies its data to `/tmp/esd`.
- Fonts: installing a font while Keynote is open has no effect until Keynote restarts. Rendering doesn't depend on it, because pages load the font themselves.
- A text helper that never sets `textContent` draws nothing and raises no error. Always look at stills.
- Speech longer than the planned animation: stretch the timeline (warp each line's start), never squeeze the voice.
- Long scenes need visible change every 2–3 s, or viewers think the video froze.

## Credits

- rough.js 4.6.6 (MIT, `assets/vendor/LICENSE-rough.txt`)
- Patrick Hand font (SIL Open Font License, `assets/fonts/OFL-PatrickHand.txt`)
- Kokoro TTS (Apache-2.0 model, used locally)
