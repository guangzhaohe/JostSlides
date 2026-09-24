# Working on JostSlides

- Keep the workflow local unless the user explicitly asks to publish or push.
- Edit deck content in `decks/<date>/deck.py`; shared presenter behavior belongs in `app/`; build logic belongs in `slidekit/`.
- Use `python slides.py new YYYY-MM-DD --title "Talk title"` for a new deck.
- Keep `META['id']` and existing slide IDs stable because browser notes are keyed to them.
- Bundle every required asset in the deck folder and record provenance in `references/SOURCES.md`.
- Use large text: at least 30 pt, concise one-line titles, and one clear takeaway per slide.
- Do not hand-edit root `index.html` or `build/`. Run `python slides.py build` after source changes.
- Run `python slides.py check` for content/layout changes and the public tests for shared runtime changes.
- Preserve the all-or-nothing startup gate: no slide may render or navigate until every required asset is ready.
- Keep presenter and audience views synchronized, while speaker notes remain presenter-only.
