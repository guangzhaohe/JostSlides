"""Build a portable HTML presentation without network access or npm dependencies."""
import base64
import html
import json
import copy
import shutil
from pathlib import Path
from urllib.parse import quote
from .project import ROOT, load_deck, validate
from .fonts import font_path


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(content)
    temp.replace(path)


def build(deck, *, output=None, activate=True):
    validate(deck)
    destination = Path(output) if output else ROOT / 'build' / deck.name
    web_slides = copy.deepcopy(deck.slides)
    active_slides = copy.deepcopy(deck.slides)
    def layers(spec):
        yield spec
        for step in spec.get('builds', []):
            if step.get('detail'):
                yield from layers(step['detail'])
    for spec, active_spec in zip(web_slides, active_slides):
        if spec.get('soundtrack'):
            source = deck.asset(spec['soundtrack']['src'])
            target = destination / spec['soundtrack']['src']
            target.parent.mkdir(parents=True, exist_ok=True)
            if source != target.resolve() and (not target.exists() or source.stat().st_size != target.stat().st_size or source.stat().st_mtime_ns != target.stat().st_mtime_ns):
                shutil.copy2(source, target)
            active_spec['soundtrack']['src'] = quote(source.relative_to(ROOT).as_posix()) if activate else quote(spec['soundtrack']['src'])
            spec['soundtrack']['src'] = quote(spec['soundtrack']['src'])
        for layer, active_layer in zip(layers(spec), layers(active_spec)):
            for picture, active_picture in zip(layer.get('images', []), active_layer.get('images', [])):
                path = deck.asset(picture['src'])
                mime = {'.svg': 'image/svg+xml', '.png': 'image/png'}.get(path.suffix.lower(), 'image/jpeg')
                picture['src'] = active_picture['src'] = f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()
            if layer.get('scene', {}).get('kind') == 'pair':
                for case, active_case in zip(layer['scene']['cases'], active_layer['scene']['cases']):
                    for frame, active_frame in zip(case['frames'], active_case['frames']):
                        path = deck.asset(frame['image'])
                        encoded = 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode()
                        frame['image'] = active_frame['image'] = encoded
            if layer.get('scene', {}).get('kind') == 'steps':
                for frame, active_frame in zip(layer['scene']['frames'], active_layer['scene']['frames']):
                    path = deck.asset(frame['image'])
                    mime = 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
                    encoded = f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()
                    frame['image'] = active_frame['image'] = encoded
        if not spec.get('video'):
            continue
        media = spec['video']
        source = deck.asset(media['src'])
        target = destination / media['src']
        target.parent.mkdir(parents=True, exist_ok=True)
        if source != target.resolve() and (not target.exists() or source.stat().st_size != target.stat().st_size or source.stat().st_mtime_ns != target.stat().st_mtime_ns):
            shutil.copy2(source, target)
        poster_path = deck.asset(media['poster'])
        mime = 'image/png' if poster_path.suffix.lower() == '.png' else 'image/jpeg'
        poster = f'data:{mime};base64,' + base64.b64encode(poster_path.read_bytes()).decode()
        active_spec['video']['src'] = quote(source.relative_to(ROOT).as_posix()) if activate else media['src']
        active_spec['video']['poster'] = poster
        media['src'] = quote(media['src'])
        media['poster'] = poster
    fonts = []
    for weight, bold in [(400, False), (700, True)]:
        encoded = base64.b64encode(font_path(deck.meta, bold, 'woff2').read_bytes()).decode()
        fonts.append(f"@font-face{{font-family:Deck;src:url(data:font/woff2;base64,{encoded}) format('woff2');font-weight:{weight};font-display:block}}")
    project_root = deck.directory.parents[1]
    deck_choices = []
    for file in sorted((project_root / 'decks').glob('*/deck.py'), reverse=True):
        choice = load_deck(file.parent.name, root=project_root)
        deck_choices.append({
            'name': choice.name,
            'title': choice.meta['title'],
            'date_label': choice.meta['date_label'],
            'url': f'/build/{choice.name}/index.html',
        })
    replacements = {
        '{{PAGE_TITLE}}': html.escape(deck.meta['title'] + ' — ' + deck.meta['date_label']),
        '{{THEME}}': html.escape(deck.meta.get('theme', 'classic'), quote=True),
        '{{DECK_TITLE}}': html.escape(deck.meta['title']),
        '{{DECK_DATE}}': html.escape(deck.meta['date_label']) if deck.meta.get('show_date', True) else '',
        '{{SLIDE_COUNT}}': str(len(deck.slides)),
        '/* EMBEDDED_FONTS */': '\n'.join(fonts),
        '/* PRESENTER_CSS */': (ROOT / 'app/presenter.css').read_text(),
        '/* WIDGETS_CSS */': (ROOT / 'app/widgets.css').read_text(),
        '/* DECK_DATA */': f'const META = {script_json(deck.meta)};\nconst DECKS = {script_json(deck_choices)};\nconst SLIDES = {script_json(web_slides)};',
        '/* WIDGETS_JS */': (ROOT / 'app/widgets.js').read_text().replace('/* EVIDENCE_DATA */', script_json(deck.evidence())),
        '/* PRESENTER_JS */': (ROOT / 'app/presenter.js').read_text(),
        '/* MOTION_JS */': (ROOT / 'app/motion/runtime.js').read_text().replace('</script', '<\\/script') if deck.meta.get('motion') == 'remotion' else '',
        '/* VIDEO_JS */': (ROOT / 'app/video.js').read_text(),
        '/* SCENES_JS */': (ROOT / 'app/scenes.js').read_text(),
        '/* AUDIO_JS */': (ROOT / 'app/audio.js').read_text(),
        '/* STARTUP_JS */': (ROOT / 'app/startup.js').read_text(),
    }
    template = (ROOT / 'app/template.html').read_text()
    # Single-pass substitution prevents meeting text from accidentally acting as a template token.
    import re
    pattern = re.compile('|'.join(re.escape(key) for key in replacements))
    rendered = pattern.sub(lambda match: replacements[match.group()], template)
    write_atomic(destination / 'index.html', rendered)
    prompts = f'# {deck.meta["title"]} — {deck.meta["date_label"]}\n\n'
    for i, slide in enumerate(deck.slides, 1):
        prompts += f'## {i}. {slide["name"]}\n\n{slide["notes"]}\n\nDiscussion notes:\n\n'
    write_atomic(destination / 'speaker-prompts.md', prompts)
    if activate:
        # Preserve the old / URL and browser-note origin for the local server.
        replacements['/* DECK_DATA */'] = f'const META = {script_json(deck.meta)};\nconst DECKS = {script_json(deck_choices)};\nconst SLIDES = {script_json(active_slides)};'
        write_atomic(ROOT / 'index.html', pattern.sub(lambda match: replacements[match.group()], template))
    return destination / 'index.html'


def capture_widgets(deck, page_path, output):
    widgets = [(i, s) for i, s in enumerate(deck.slides) if s.get('widget') or s.get('scene')]
    if not widgets:
        return
    from playwright.sync_api import sync_playwright
    directory = output / 'widget-previews'
    directory.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1152, 'height': 648})
        page.goto(page_path.resolve().as_uri() + '?audience=1')
        page.wait_for_function('presentationReady === true')
        page.add_style_tag(content='.audience-fullscreen{display:none!important}')
        for i, slide in widgets:
            page.evaluate('i=>go(i)', i)
            page.locator('#slide .scene-view' if slide.get('scene') else '#slide .evidence').screenshot(path=str(directory / (slide['id'] + '.jpg')), type='jpeg', quality=90)
        browser.close()
