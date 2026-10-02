# JostSlides: the interactive showcase

A 22-slide, five-to-seven-minute promo example using circles, squares, cubes, and toy data. It keeps the original example’s black canvas, large Jost type, dark panels, and mint, gold, pink, and blue accents.

## Run it

From the repository root, with the optional requirements installed for checks and export:

```bash
python slides.py check
python slides.py build
python slides.py serve
```

Open <http://localhost:8769>. Start an **Audience window** and try the demo controls; speaker prompts explain each action. External source links need a connection, while the presentation itself is bundled locally.

## Feature tour

| Slides | Try this | Authoring fields |
| --- | --- | --- |
| 1–3 | Cover particles, native shapes, automatic Remotion transitions | `cover_particles`, `vectors`, `META['motion']` |
| 4 | Reveal, play/restart steps, open a detail and return with Esc | `builds`, `text`, `rects`, `detail` |
| 5 | Play/seek a video; let the end advance the slide | `video`, `autoplay`, `next` |
| 6–7 | Loop a dimmed background video, change music volume, continue audio across slides; view a cropped SVG | `background`, `dim`, `loop`, `soundtrack`, `images`, `fit` |
| 8–9 | Drag/reset a cloud; compare raw and aligned scale | `scene: cloud`, `prediction_points`, `alignment_scale` |
| 10–11 | Adjust scale/shift and camera-ambiguity sliders | `scene: normalized-shift`, `scene: ambiguity` |
| 12 | Orbit before/after overlays together | `scene: correction` |
| 13 | Play/scrub a sequence beside a still; orbit each cloud | `scene: pair` |
| 14 | Browse image stages | `scene: steps` |
| 15 | Filter cases, select plot points, tune a rejection policy | `widget: diode` |
| 16–17 | Select endpoint measurements and compare accepted/rejected results | `widget: real`, `widget: predictions` |
| 18 | Write private notes, export a backup, open the synchronized audience view | `notes`, stable deck and slide IDs |
| 19 | Overview, keyboard navigation, fullscreen, note toggle, question highlight | Presenter toolbar and question text |
| 20 | Open source context and clickable links | `sources` |
| 21–22 | Author/check/build/export; make the example your own | `deck.py`, `slides.py` |

HTML retains interactive demos. PDF and PPTX use demo snapshots; PPTX text and rectangles stay editable and videos are embedded. Run `python slides.py export` to create the shareable files under `build/2026-09-24/`.

Use the header deck picker to switch to [A tiny talk](../2026-10-02/README.md), a six-slide starter with a literal Python-to-slide example and no media dependencies. Notes remain separate across decks.

## Original, reproducible fixtures

All numerical data is synthetic and labeled as toy evidence. The drawn dimensions are assigned values, not physical measurements. No research benchmark, model output, paper figure, or third-party video is included.

- `media/demo/` contains native SVG stages, raster captures, a four-second primitive video, and an eight-second synthesized chord.
- `evidence/` contains sampled primitive clouds, a frame sequence, and frozen widget fixtures.
- `scripts/make_demo_assets.py` reproduces these assets locally with Playwright/Chromium and ffmpeg. Those dependencies are only needed to regenerate assets; the committed assets support normal builds.
- `references/SOURCES.md` records provenance and transformations.

## Note compatibility

The existing dated folder, `META['id']`, and retained slide IDs deliberately remain unchanged. Historical `moge*` storage keys do not describe the new slide titles. Notes for the twelve removed slides remain in browser storage and are included as archived slides in **Export all notes**. Export a backup before clearing browser data or changing machines.
