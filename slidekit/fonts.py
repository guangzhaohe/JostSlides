"""Bundled fonts shared by browser slides, bounds checks and exports."""
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parents[1] / 'app' / 'fonts'


def font_family(meta):
    family = meta.get('font', 'DejaVu Sans')
    if family not in ('Jost', 'DejaVu Sans'):
        raise ValueError(f'Unsupported bundled font: {family}')
    return family


def font_path(meta, bold=False, extension='ttf'):
    stem = 'Jost' if font_family(meta) == 'Jost' else 'DejaVuSans'
    return FONT_DIR / f'{stem}{"-Bold" if bold else ""}.{extension}'
