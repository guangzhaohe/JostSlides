"""Compatibility helper for capturing the default deck's interactive panels."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slidekit.project import load_deck
from slidekit.build import build, capture_widgets
if __name__ == '__main__':
    deck = load_deck()
    page = build(deck)
    capture_widgets(deck, page, page.parent)
