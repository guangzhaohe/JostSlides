# Showcase source record

Created October 2, 2026. This example replaces the former MoGe research talk with original primitives and synthetic fixtures. Every presentation asset is bundled locally.

## Artwork and motion

- `media/demo/stage-0.svg` through `stage-3.svg` are original SVG primitives: an empty canvas, a square, a circle, and cube faces. Their PNG counterparts are Chromium raster captures.
- `media/demo/objects-0.jpg` through `objects-2.jpg` are Chromium JPEG captures of color variants of the same SVG primitive scene. The asset generator embeds these images into the frozen widget JSON so startup can inventory and decode them.
- `media/demo/primitives.mp4` is an original four-second animation of a circle, square, and triangle. The generator renders 96 deterministic frames on a browser canvas, then encodes H.264 at 24 fps with ffmpeg. `motion-poster.png` is frame zero.
- `media/demo/chord.wav` is an original eight-second synthesized chord at 220, 275, and 330 Hz with short fades, generated using ffmpeg. It contains no recorded or third-party audio.
- Cover particles, native shapes, transitions, builds, and scientific scenes use this repository’s existing local rendering and Remotion runtime. No external image generation or source artwork was used.

## Toy data

- `evidence/primitive-cloud.json` samples a cube shell, sphere, and plane analytically. Colors identify the primitive surfaces.
- `evidence/primitive-sequence.json` stores three rotations and the corresponding primitive-image paths. It is an illustrative sequence, not measured reconstruction data.
- `evidence/toy-evidence.json` contains ten synthetic diagnostic cases and four assigned dimensions across two toy scenes. Error percentages are fixture arithmetic. Indoor/outdoor tags are test categories, not claims about the artwork. The first measurement scene is corrected exactly; the second is deliberately corrected incorrectly to demonstrate rejected diagnostics.
- The comparison input is the reference cloud divided by 1.6. Applying 1.6 restores it exactly; this is an algebraic illustration, not an empirical result.
- The camera ambiguity and normalized-shift scenes are original analytic teaching diagrams already implemented in `app/scenes.js`. The normalized-shift interaction originated in the previous example, which explained pinhole projection using [MoGe 1, Section 3.1](https://arxiv.org/abs/2410.19115). No paper artwork, figures, or numerical results are retained.

All fixtures are reproduced by [`scripts/make_demo_assets.py`](../scripts/make_demo_assets.py), using Python's standard library, Playwright/Chromium, and ffmpeg. External source links on the deck point to the [JostSlides repository](https://github.com/guangzhaohe/JostSlides) and its documentation.

## Bundled dependencies

Jost fonts and their license remain under `app/fonts/`. Remotion, React, and scheduler notices remain under `app/motion/licenses/`.
