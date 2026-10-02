"""Public examples, note compatibility, and complete feature coverage."""
import unittest
from slidekit.project import DEFAULT_DECK, ROOT, WIDGETS, load_deck, validate


class PublicProjectTest(unittest.TestCase):
    def test_public_examples_are_present(self):
        names = sorted(p.parent.name for p in (ROOT / 'decks').glob('*/deck.py'))
        self.assertEqual(names, ['2026-09-24', '2026-10-02'])
        self.assertEqual(DEFAULT_DECK, '2026-09-24')
        ids = []
        for name in names:
            deck = load_deck(name)
            validate(deck, text_bounds=True)
            ids.append(deck.meta['id'])
            self.assertTrue((deck.directory / 'references/SOURCES.md').is_file())
        self.assertEqual(len(ids), len(set(ids)))

    def test_showcase_covers_supported_features(self):
        deck = load_deck()
        self.assertEqual(deck.meta['id'], 'accidental-size-probes-2026-09-24')
        self.assertEqual(deck.meta['motion'], 'remotion')
        self.assertEqual(len(deck.slides), 22)
        self.assertEqual({s['scene']['kind'] for s in deck.slides if s.get('scene')},
                         {'cloud', 'normalized-shift', 'ambiguity', 'correction', 'pair', 'steps'})
        self.assertEqual({s['widget'] for s in deck.slides if s.get('widget')}, WIDGETS)
        self.assertTrue(any(s.get('cover_particles') for s in deck.slides))
        self.assertTrue(any(s.get('vectors') for s in deck.slides))
        self.assertTrue(any(s.get('images') for s in deck.slides))
        self.assertTrue(any(s.get('video', {}).get('next') for s in deck.slides))
        self.assertTrue(any(s.get('video', {}).get('background') for s in deck.slides))
        self.assertTrue(any(step.get('detail') for s in deck.slides for step in s.get('builds', [])))
        sounds = [s['soundtrack']['src'] for s in deck.slides if s.get('soundtrack')]
        self.assertEqual(len(sounds), 2)
        self.assertEqual(sounds[0], sounds[1])
        evidence = deck.evidence()
        self.assertEqual(len(evidence['diode']['cases']), 10)
        self.assertEqual(sum(len(s['measurements']) for s in evidence['real']), 4)
        self.assertTrue(all(s['notes'] for s in deck.slides))
        self.assertTrue(all(s['sources'] for s in deck.slides))
        self.assertTrue(all('Toy' in s['name'] for s in deck.slides if s.get('widget')))

    def test_starter_has_an_independent_note_namespace(self):
        tiny = load_deck('2026-10-02')
        self.assertEqual(len(tiny.slides), 6)
        self.assertNotEqual(tiny.meta['id'], load_deck().meta['id'])
        self.assertEqual(tiny.slides[0]['id'], 'recap')
        example = next(s for s in tiny.slides if s['id'] == 'python-to-slide')
        self.assertIn((624, 256, 400, 64*1.3, 'Hello', 64, True, 'B8E3D1'), example['text'])


if __name__ == '__main__':
    unittest.main()
