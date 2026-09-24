# Fantastic MoGEs and Where to Find Them

This 34-slide research presentation follows one technical thread across MoGe 1, MoGe 2, and MoGe 3. Each section leads with outputs and evidence, then explains the problem, method, training details, limitations, and lessons for future geometry training.

The three sections are:

1. **MoGe 1:** affine-invariant point maps, focal-distance ambiguity, robust alignment, and local supervision
2. **MoGe 2:** decoupled metric scale and synthetic-guided refinement of real labels
3. **MoGe 3:** iterative sparse 3D refinement for thin structures and boundaries

The deck includes official paper figures and videos, locally sampled demonstration point clouds, an interactive normalized-shift explanation, MoGe 3 refinement stages, quantitative results, and speaker notes with protocol caveats.

## Run the deck

From the repository root:

```bash
python slides.py check
python slides.py build
python slides.py serve
```

Open <http://localhost:8769>. Rebuild and refresh the same tab after editing to preserve browser-local notes.

## Files

- [`deck.py`](deck.py) contains the slides, order, notes, and source links
- [`media/`](media/) contains every image and video required during startup
- [`evidence/`](evidence/) contains sampled point clouds for offline viewers
- [`references/SOURCES.md`](references/SOURCES.md) records provenance and transformations
- [`scripts/import_glb_cloud.py`](scripts/import_glb_cloud.py) converts an author-hosted GLB mesh into the lightweight JSON viewer format

Keep `META['id']` and existing slide IDs stable because notes are keyed to them. Add new material with new IDs, then run `python slides.py check` before presenting or exporting.
