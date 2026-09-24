"""Public repository structure, metadata, assets, and deck invariants."""
from pathlib import Path
import unittest

from slidekit.project import DEFAULT_DECK, ROOT, load_deck, validate


class PublicProjectTest(unittest.TestCase):
    def test_only_public_deck_is_present(self):
        decks = sorted(path.parent.name for path in (ROOT / 'decks').glob('*/deck.py'))
        self.assertEqual(decks, ['2026-09-24'])
        self.assertEqual(DEFAULT_DECK, '2026-09-24')

    def test_public_deck_is_complete(self):
        deck = load_deck()
        validate(deck, text_bounds=True)
        ids = [slide['id'] for slide in deck.slides]
        self.assertEqual(len(ids), 34)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('moge1-normalized-shift', ids)
        self.assertIn('moge3-method', ids)
        self.assertNotIn('moge2-demo', ids)
        method = next(slide for slide in deck.slides if slide['id'] == 'moge3-method')
        self.assertEqual(method['images'][0]['src'], 'media/moge3/method.svg')

    def test_only_public_source_tree_is_present(self):
        self.assertEqual(
            sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / 'decks').glob('*/deck.py')),
            ['decks/2026-09-24/deck.py'],
        )


if __name__ == '__main__':
    unittest.main()
