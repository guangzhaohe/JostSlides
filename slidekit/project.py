"""Deck discovery and validation. This module requires only Python's standard library."""
from dataclasses import dataclass
from datetime import date
import importlib.util
import json
import math
from pathlib import Path
import re
from .fonts import font_family, font_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECK = '2026-09-24'
WIDGETS = {'diode', 'real', 'predictions'}

@dataclass
class Deck:
    directory: Path
    meta: dict
    slides: list
    evidence_files: dict

    @property
    def name(self):
        return self.directory.name

    def evidence(self):
        data = {}
        for key, relative in self.evidence_files.items():
            path = (self.directory / relative).resolve()
            if not path.is_relative_to(self.directory.resolve()):
                raise ValueError(f'Evidence must be inside the deck folder: {relative}')
            loaded = json.loads(path.read_text())
            if key == 'snapshot':
                data.update(loaded)
            else:
                data[key] = loaded
        return data

    def asset(self, relative):
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('Media paths must be relative to the deck folder')
        path = (self.directory / relative).resolve()
        if not path.is_relative_to(self.directory.resolve()) or not path.is_file():
            raise ValueError(f'Missing or external deck media: {relative}')
        return path


def load_deck(name=DEFAULT_DECK, *, root=ROOT):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', name):
        raise ValueError('Choose a deck folder named YYYY-MM-DD')
    date.fromisoformat(name)
    directory = root / 'decks' / name
    path = directory / 'deck.py'
    if not path.is_file():
        raise ValueError(f'Deck not found: {path}')
    spec = importlib.util.spec_from_file_location('meeting_' + name.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    deck = Deck(directory, module.META, module.SLIDES, getattr(module, 'EVIDENCE', {}))
    validate(deck)
    return deck


def validate(deck, *, text_bounds=False):
    meta = deck.meta
    font_family(meta)
    if meta.get('theme', 'classic') not in ('classic', 'black'):
        raise ValueError('Theme must be classic or black')
    for key in ['id', 'title', 'date', 'date_label', 'export_stem']:
        if not isinstance(meta.get(key), str) or not meta[key]:
            raise ValueError(f'Missing deck metadata: {key}')
    for key in ['id', 'export_stem']:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', meta[key]):
            raise ValueError(f'{key} must contain only lowercase letters, digits and hyphens')
    if meta['date'] != deck.name:
        raise ValueError('META.date must match the meeting folder')
    if not isinstance(deck.slides, list) or not deck.slides:
        raise ValueError('A deck needs at least one slide')
    ids = set()
    for slide in deck.slides:
        identity = slide.get('id', '')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', identity) or identity in ids:
            raise ValueError(f'Invalid or duplicate slide ID: {identity}')
        ids.add(identity)
        if not isinstance(slide.get('name'), str) or not isinstance(slide.get('notes'), str):
            raise ValueError(f'{identity}: name and notes must be text')
        if not re.fullmatch(r'[0-9A-Fa-f]{6}', slide.get('bg', '')):
            raise ValueError(f'{identity}: invalid background color')
        if 'builds' in slide:
            if not isinstance(slide['builds'], list) or not slide['builds'] or slide.get('video') or slide.get('widget'):
                raise ValueError(f'{identity}: builds need nonempty steps on a text/shape slide')
            used = {'text': set(), 'rects': set()}
            for step in slide['builds']:
                if not isinstance(step.get('label'), str) or not step['label'].strip():
                    raise ValueError(f'{identity}: each build step needs a label')
                x, y, w, h = step['bounds']
                if min(x, y) < 0 or min(w, h) <= 0 or x+w > 1152 or y+h > 648:
                    raise ValueError(f'{identity}: build target outside the canvas')
                for kind in used:
                    for index in step.get(kind, []):
                        if type(index) is not int or not 0 <= index < len(slide.get(kind, [])) or index in used[kind]:
                            raise ValueError(f'{identity}: invalid or repeated build {kind} index')
                        used[kind].add(index)
                if step.get('detail'):
                    validate(Deck(deck.directory, deck.meta, [step['detail']], {}), text_bounds=text_bounds)
        for tag, attributes in slide.get('vectors', []):
            allowed = {'x','y','width','height','rx','x1','y1','x2','y2','cx','cy','r','points','fill','stroke','stroke-width'}
            if tag not in ('line','circle','rect','polyline','polygon') or not set(attributes) <= allowed:
                raise ValueError(f'{identity}: unsupported vector primitive')
        if slide.get('widget') and slide['widget'] not in WIDGETS:
            raise ValueError(f'{identity}: unknown widget {slide["widget"]}')
        if slide.get('scene'):
            scene = slide['scene']
            if scene.get('kind') not in ('ambiguity', 'normalized-shift', 'cloud', 'pair', 'correction', 'steps') or any(slide.get(k) for k in ('widget', 'video', 'builds')):
                raise ValueError(f'{identity}: unsupported or conflicting scientific scene')
            x,y,w,h = scene.get('bounds', [48,168,1056,400])
            if min(x,y) < 0 or w <= 0 or h <= 54 or x+w > 1152 or y+h > 648:
                raise ValueError(f'{identity}: scene outside the canvas')
            clouds = []
            if scene['kind'] == 'cloud':
                clouds = [scene]
                if scene.get('prediction_points'):
                    prediction = scene['prediction_points']
                    if len(prediction) != len(scene.get('points', [])) or not math.isfinite(scene.get('alignment_scale', 0)) or scene['alignment_scale'] <= 0:
                        raise ValueError(f'{identity}: invalid comparison cloud')
                    if any(len(p) != 3 or not all(math.isfinite(v) for v in p) for p in prediction):
                        raise ValueError(f'{identity}: invalid prediction coordinates')
            if scene['kind'] == 'correction':
                gt, prediction = scene.get('ground_truth', []), scene.get('prediction', [])
                if not gt or len(gt) != len(prediction) or not math.isfinite(scene.get('applied_scale', 0)) or scene['applied_scale'] <= 0:
                    raise ValueError(f'{identity}: invalid paired correction')
                if any(len(p) != 3 or not all(math.isfinite(v) for v in p) for p in gt + prediction):
                    raise ValueError(f'{identity}: invalid correction coordinates')
            if scene['kind'] == 'pair':
                cases = scene.get('cases', [])
                if len(cases) != 2:
                    raise ValueError(f'{identity}: scene needs two cases')
                for case in cases:
                    if not case.get('label') or not case.get('frames'):
                        raise ValueError(f'{identity}: gallery case needs label and frames')
                    view = case.get('view', {})
                    if (len(view.get('center', [])) != 3 or len(view.get('projection_center', [])) != 2
                            or not all(math.isfinite(v) for v in [*view['center'], *view['projection_center']])
                            or not math.isfinite(view.get('radius', 0)) or view['radius'] <= 0
                            or not math.isfinite(view.get('fit', 0)) or view['fit'] <= 0):
                        raise ValueError(f'{identity}: invalid fixed camera view')
                    for frame in case['frames']:
                        deck.asset(frame['image'])
                        clouds.append(frame)
            if scene['kind'] == 'steps':
                frames = scene.get('frames', [])
                if len(frames) < 2 or any(not frame.get('label') for frame in frames):
                    raise ValueError(f'{identity}: step scene needs at least two labeled frames')
                for frame in frames:
                    deck.asset(frame['image'])
            for cloud in clouds:
                points, colors = cloud.get('points', []), cloud.get('colors', [])
                if not points or len(points) != len(colors):
                    raise ValueError(f'{identity}: point cloud needs matching points and colors')
                for point, color in zip(points, colors):
                    if len(point) != 3 or len(color) != 3 or not all(math.isfinite(v) for v in point) or not all(isinstance(v, int) and 0 <= v <= 255 for v in color):
                        raise ValueError(f'{identity}: invalid point cloud coordinates or colors')
        for picture in slide.get('images', []):
            deck.asset(picture['src'])
            x, y, w, h = picture['bounds']
            if min(x, y) < 0 or min(w, h) <= 0 or x+w > 1152 or y+h > 648:
                raise ValueError(f'{identity}: image outside the canvas')
        if slide.get('video'):
            media = slide['video']
            if media.get('next') and not any(s.get('id') == media['next'] for s in deck.slides):
                raise ValueError(f'{identity}: missing next video slide')
            dim = media.get('dim', 0)
            if not isinstance(dim, (int, float)) or not 0 <= dim <= 1:
                raise ValueError(f'{identity}: video dim must be between 0 and 1')
            if slide.get('widget'):
                raise ValueError(f'{identity}: video and widget cannot share a slide')
            for key in ('src', 'poster'):
                if key not in media:
                    raise ValueError(f'{identity}: video needs {key}')
                deck.asset(media[key])
            x, y, w, h = media.get('bounds', [0, 0, 1152, 648])
            if min(x, y) < 0 or min(w, h) <= 0 or x+w > 1152 or y+h > 648:
                raise ValueError(f'{identity}: video outside the canvas')
        if slide.get('soundtrack'):
            deck.asset(slide['soundtrack']['src'])
            volume = slide['soundtrack'].get('volume', 0.08)
            if not isinstance(volume, (int, float)) or not 0 <= volume <= 1:
                raise ValueError(f'{identity}: soundtrack volume must be between 0 and 1')
        for x, y, w, h, text, size, bold, color in slide['text']:
            if meta.get('theme') == 'black' and any(dot in text for dot in ('·', '•', '‧', '∙', '⋅')):
                raise ValueError(f'{identity}: use words or commas instead of center dots: {text}')
            if size < 30 or min(x, y, w, h) < 0 or x+w > 1152 or y+h > 648:
                raise ValueError(f'{identity}: text too small or outside the canvas: {text}')
            if text_bounds:
                from PIL import ImageFont
                font = font_path(meta, bold)
                if ImageFont.truetype(str(font), size).getlength(text) > w:
                    raise ValueError(f'{identity}: text is wider than its box: {text}')
    if text_bounds:
        evidence = deck.evidence()
        for slide in deck.slides:
            widget = slide.get('widget')
            required = {'diode': ['diode'], 'real': ['real'], 'predictions': ['real', 'real_results']}.get(widget, [])
            if any(key not in evidence for key in required):
                raise ValueError(f'{slide["id"]}: missing evidence for {widget}')
