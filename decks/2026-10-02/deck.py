"""A six-slide starter talk, created with slides.py new. No media dependencies."""
from slidekit.dark import ACCENT, MUTED, PANEL, slide, t

META = {
    'id': 'a-tiny-talk-2026-10-02', 'title': 'A tiny talk',
    'date': '2026-10-02', 'date_label': 'October 2, 2026',
    'export_stem': 'a-tiny-talk-2026-10-02', 'theme': 'black',
    'font': 'Jost', 'motion': 'remotion',
}
EVIDENCE = {}
REPO = 'https://github.com/guangzhaohe/JostSlides'

SLIDES = [
    slide('recap', 'A tiny talk', [
        t(64, 166, 'A tiny talk', 80, True),
        t(64, 300, 'One idea. Six slides. Ready to adapt.', 42, True, color=ACCENT),
        t(64, 504, 'A minimal example written entirely in Python', 32, color=MUTED),
    ], notes='This second example is a tiny talk that you can adapt without media or evidence files. Use the deck picker to return to the full feature showcase. Its independent deck ID keeps notes separate, even though it reuses recap and discussion slide IDs.', sources=[('JostSlides',REPO)]),
    slide('one-idea', 'Give each slide one idea', [
        t(64, 54, 'Give each slide one idea', 54, True),
        t(64, 204, 'Lead with the point', 46, True, color=ACCENT),
        t(64, 300, 'Keep the supporting text short and readable', 34),
        t(64, 480, 'Leave room for the audience to think', 34, color=MUTED),
    ], notes='A plain text slide using the same large typography as the full showcase. Replace the point and support with your own talk content.'),
    slide('python-to-slide', 'Python becomes the slide', [
        t(64, 54, 'Python becomes the slide', 54, True),
        t(64, 160, 'Source', 38, True, color=ACCENT, width=470),
        t(64, 256, "t(624, 256, 'Hello',", 32, width=470),
        t(64, 310, '  64, True, color=ACCENT,', 32, width=470),
        t(64, 364, '  width=400)', 32, width=470),
        t(624, 160, 'Result', 38, True, color='EC93D7', width=400),
        t(624, 256, 'Hello', 64, True, color=ACCENT, width=400),
        t(64, 536, 'Edit the text, rebuild, and the slide changes', 32, color=MUTED),
    ], [(592,220,480,240,PANEL)], notes='The code on the left is the exact t call used for the Hello text on the right. The result is an editable slide text object, not a screenshot. Position, size, weight, color, and width are explicit.'),
    slide('progress', 'Reveal the argument in steps', [
        t(64, 54, 'Reveal the argument in steps', 54, True),
        t(90, 190, '1  State the idea', 42, True, color=ACCENT),
        t(90, 306, '2  Show the evidence', 42, True, color='EBCB8B'),
        t(90, 422, '3  Ask for a decision', 42, True, color='EC93D7'),
        t(64, 564, 'Press Right Arrow or use Play steps', 32, color=MUTED),
    ], [(64,166,1024,88,PANEL),(64,282,1024,88,PANEL),(64,398,1024,88,PANEL)], builds=[
        {'label':'Idea','bounds':[64,166,1024,88],'text':[1],'rects':[0]},
        {'label':'Evidence','bounds':[64,282,1024,88],'text':[2],'rects':[1]},
        {'label':'Decision','bounds':[64,398,1024,88],'text':[3],'rects':[2]},
    ], notes='Use the same build machinery as the full showcase with a simpler vertical layout. Arrow navigation advances steps before leaving the slide. The audience sees the same step.'),
    slide('two-options', 'Compare two options clearly', [
        t(64, 54, 'Compare two options clearly', 54, True),
        t(90, 210, 'Keep it simple', 40, True, color=ACCENT, width=440),
        t(90, 296, 'Text, shapes, and notes', 34, width=440),
        t(90, 370, 'A quick talk or meeting', 34, width=440),
        t(630, 210, 'Add a live demo', 40, True, color='EC93D7', width=440),
        t(630, 296, 'Media or interactive evidence', 32, width=440),
        t(630, 370, 'The full showcase has examples', 30, width=440),
    ], [(64,174,500,310,PANEL),(604,174,484,310,PANEL)], notes='Two matched panels for a meaningful comparison. The feature showcase demonstrates the optional media and interactive machinery. This starter stays deliberately small.'),
    slide('discussion', 'What should we try next', [
        t(64, 100, 'What should we try next', 62, True),
        t(64, 256, 'Which idea deserves its own slide?', 42, True, color=ACCENT),
        t(64, 384, 'Write the decision in presenter notes', 36),
        t(64, 516, 'Switch decks to explore the complete showcase', 32, color=MUTED),
    ], notes='Click the question to highlight it. Capture a decision in the private note field. Switch to the other example using the header deck picker: the note you wrote here remains tied to this deck.', sources=[('Feature showcase source',REPO+'/tree/main/decks/2026-09-24')]),
]
