# Authoring decks

Each presentation lives in a dated folder and remains self-contained:

```text
decks/YYYY-MM-DD/
├── deck.py
├── media/
├── evidence/
├── references/
└── scripts/
```

## Create a deck

```bash
python slides.py new 2026-10-01 --title "My research talk"
python slides.py check --deck 2026-10-01
python slides.py serve --deck 2026-10-01
```

`deck.py` exports four values:

- `META`: title, date, stable note-storage ID, theme, font, and optional motion mode
- `EVIDENCE`: optional names mapped to deck-relative JSON files
- `SLIDES`: the ordered slide specifications
- Any local helpers used to make the specifications concise

## A minimal slide

```python
from slidekit.dark import t, slide, ACCENT

SLIDES.append(slide(
    'one-stable-id',
    'One clear takeaway',
    [
        t(64, 54, 'One clear takeaway', 52, True),
        t(64, 220, 'Support it with one concise piece of evidence', 36),
        t(64, 520, 'Lead naturally into the next slide', 32, color=ACCENT),
    ],
    notes='Context, caveats, and source details belong in speaker notes.',
    sources=[('Paper or project page', 'https://example.org')],
))
```

The canvas is 1152 × 648. Text boxes use `x, y, text, size`; optional arguments control weight, color, and width. Keep visible text at 30 pt or larger. Prefer removing content over shrinking it.

## IDs and notes

`META['id']` identifies the deck in browser local storage. Each slide ID identifies that slide’s notes. Keep both stable when reordering or temporarily removing slides. New slides need unique lowercase hyphenated IDs.

## Media

Images are bundled into the generated HTML:

```python
images=[{
    'src': 'media/result.png',
    'bounds': [64, 130, 1024, 400],
    'alt': 'Description of the result',
    'fit': 'contain',
}]
```

Videos remain local files beside the generated HTML so the browser can preload and seek them efficiently:

```python
video={
    'src': 'media/demo.mp4',
    'poster': 'media/demo.jpg',
    'bounds': [96, 128, 960, 480],
    'autoplay': False,
    'muted': True,
}
```

Every asset needed during the talk must be inside the deck folder. The startup gate intentionally treats missing media as a hard failure.

## Scientific scenes

A slide may provide a `scene` specification. Shared rendering lives in `app/scenes.js`; validation lives in `slidekit/project.py`. The public showcase demonstrates all supported scene kinds:

- Interactive point clouds, including raw/aligned comparison
- Before/after correction with a shared orbit
- Paired still and sequence galleries
- Generic image stages
- Camera-projection ambiguity
- Normalized scale and shift

The showcase also exercises all three evidence widgets with explicitly synthetic JSON fixtures. See the [feature index](../decks/2026-09-24/README.md) for controls and examples, or [A tiny talk](../decks/2026-10-02/README.md) for a minimal Python source example. The local header picker switches decks while keeping their note namespaces separate.

When adding a scene kind, add validation, accessible controls, state synchronization through `widgetState.scenes`, and a browser regression test.

## Motion

Set `META['motion'] = 'remotion'` to use the bundled runtime. Navigation automatically starts the incoming slide’s animation and holds its completed state.

Editing the motion source requires Node:

```bash
npm ci --prefix app/motion
# Edit app/motion/index.jsx
npm run build --prefix app/motion
python slides.py build
```

Normal building and presenting do not require Node because `app/motion/runtime.js` is committed.

## Check and export

```bash
python slides.py check --deck YYYY-MM-DD
python slides.py build --deck YYYY-MM-DD
python slides.py export --deck YYYY-MM-DD
```

`check` validates stable IDs, readable text, canvas bounds, and local assets. `export` creates PDF, PPTX, previews, widget snapshots, and speaker prompts under `build/<date>/`.
