"""Black slide defaults for new talks on the existing 1152 × 648 canvas."""
from . import design

BLACK = '000000'
WHITE = 'F5F5F5'
MUTED = 'C2C2C2'
ACCENT = 'B8E3D1'
PANEL = '171717'


def t(x, y, content, size=36, bold=False, color=WHITE, width=1024):
    return design.t(x, y, content, size, bold, color, width)


def lines(x, y, content, size=36, bold=False, color=WHITE, width=1024, leading=None):
    return design.lines(x, y, content, size, bold, color, width, leading)


def slide(id, name, text, rects=(), notes='', bg=BLACK, **extra):
    return design.slide(id, name, text, rects, notes, bg, **extra)
