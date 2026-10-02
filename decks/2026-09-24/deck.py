"""A compact hands-on showcase. Historical IDs remain stable for browser notes."""
import json
from pathlib import Path
from slidekit.dark import t, lines, slide, MUTED, ACCENT, PANEL

ROOT = Path(__file__).parent
META = {
    'id': 'accidental-size-probes-2026-09-24',
    'title': 'JostSlides: the interactive showcase',
    'date': '2026-09-24', 'date_label': 'September 24, 2026',
    'show_date': True, 'export_stem': 'jostslides-showcase',
    'theme': 'black', 'font': 'Jost', 'motion': 'remotion',
}
EVIDENCE = {'snapshot': 'evidence/toy-evidence.json'}
TEAL, GOLD, PINK, BLUE = ACCENT, 'EBCB8B', 'EC93D7', '8CB8FF'
REPO = 'https://github.com/guangzhaohe/JostSlides'
DOCS = [('JostSlides source and guide', REPO)]
cloud = json.loads((ROOT / 'evidence/primitive-cloud.json').read_text())
sequence = json.loads((ROOT / 'evidence/primitive-sequence.json').read_text())
prediction = [[v / 1.6 for v in point] for point in cloud['points']]
soundtrack = {'src': 'media/demo/chord.wav', 'volume': .12}


def title(text, size=52):
    return t(64, 44, text, size, True)


def picture(src, bounds, alt, **options):
    return dict(src=src, bounds=bounds, alt=alt, **options)


def primitive(tag, **attributes):
    return tag, attributes


def panel(x, heading, body, color):
    return [t(x+26, 198, heading, 38, True, color=color, width=260),
            *lines(x+26, 288, body, 32, width=260, leading=48)]


SLIDES = [
    slide('recap', 'JostSlides', [
        t(64, 156, 'JostSlides', 80, True, width=600),
        *lines(64, 282, ['A small deck', 'A lot to try'], 48, True, width=600, leading=64),
        t(64, 512, '22 slides, one hands-on tour', 32, color=MUTED),
    ], cover_particles=True, vectors=[
        primitive('circle', cx=858, cy=230, r=68, fill='#b8e3d1'),
        primitive('rect', x=744, y=352, width=124, height=124, fill='#ebcb8b'),
        primitive('polygon', points='958,326 1038,466 878,466', fill='#ec93d7'),
    ], notes='A five-to-seven-minute feature tour. Shapes, sound, and numerical examples are original toy fixtures. Navigate with Right Arrow or Space. Open an audience window early to show synchronized interactions.', sources=DOCS),

    slide('series-map', 'A presentation you can explore', [
        title('A presentation you can explore'),
        *panel(64, 'Motion', ['Automatic entry', 'Step reveals', 'Video + sound'], TEAL),
        *panel(412, 'Interaction', ['Sliders + orbit', 'Evidence filters', 'Live comparisons'], GOLD),
        *panel(760, 'Presenter', ['Private notes', 'Audience sync', 'Links + exports'], PINK),
        t(64, 552, 'Try each feature as we go', 34, color=MUTED),
    ], [(x, 172, 304, 328, PANEL) for x in (64, 412, 760)],
    notes='Everything listed here is exercised in the following slides. Each interactive demo includes an action to try. Numerical examples are synthetic, not research results.', sources=DOCS),

    slide('moge1-section', 'Automatic transitions', [
        t(64, 152, 'Automatic transitions', 66, True, color=TEAL),
        t(64, 284, 'Move forward. The slide animates itself.', 40, True),
        t(64, 370, "META['motion'] = 'remotion'", 34, color=GOLD),
        t(64, 536, 'Text, shapes, and images arrive together', 32, color=MUTED),
    ], vectors=[primitive('circle', cx=982, cy=412, r=52, fill='#ec93d7')],
    notes='Go back to slide 2, then advance again to show automatic Remotion motion. The bundled runtime starts on entry and settles into the destination. Reduced-motion preferences are respected. Ordinary slides have transitions; scenes, videos, widgets, and builds use their own interaction/playback behavior.', sources=DOCS),

    slide('moge1-ambiguity', 'Reveal one step at a time', [
        title('Reveal one step at a time'),
        t(90, 214, '1  Compose', 38, True, color=TEAL, width=260),
        t(90, 292, 'Write Python', 32, width=260),
        t(438, 214, '2  Reveal', 38, True, color=GOLD, width=260),
        t(438, 292, 'Add build steps', 32, width=260),
        t(786, 214, '3  Explore', 38, True, color=PINK, width=260),
        t(786, 292, 'Open a detail', 32, width=260),
        t(64, 524, 'Click the canvas or use Play steps', 34, color=MUTED),
    ], [(x, 174, 304, 276, PANEL) for x in (64, 412, 760)], builds=[
        {'label': 'Compose', 'bounds': [64,174,304,276], 'text': [1,2], 'rects': [0]},
        {'label': 'Reveal', 'bounds': [412,174,304,276], 'text': [3,4], 'rects': [1]},
        {'label': 'Explore', 'bounds': [760,174,304,276], 'text': [5,6], 'rects': [2],
         'detail': slide('showcase-build-detail', 'A detail inside a slide', [
             title('A detail inside a slide'),
             t(64, 178, 'This view belongs to the third build step', 38, True, color=PINK),
             t(64, 278, "{'label': 'Explore',", 34, color=TEAL),
             t(64, 338, " 'text': [5, 6], 'rects': [2],", 34, color=TEAL),
             t(64, 398, " 'detail': slide(...)}", 34, color=TEAL),
             t(64, 548, 'Press Esc or choose Pipeline overview to return', 32, color=MUTED),
         ], notes='A detail slide embedded in a build group. It shares the main slide note key and navigation context.')},
    ], notes='Use Right Arrow twice or Play steps. Restart steps replays the reveals. Click the third panel or Explore step to open its detail. Escape returns to the overview. Build steps and detail views synchronize with the audience.', sources=DOCS),

    slide('moge1-video', 'Local video, live playback', [
        title('Local video, live playback'),
        t(64, 574, 'Press play, seek, or wait for the next slide', 32, color=MUTED),
    ], video={'src':'media/demo/primitives.mp4', 'poster':'media/demo/motion-poster.png',
              'bounds':[128,124,896,420], 'autoplay':False, 'muted':True, 'next':'moge1-results'},
    notes='Play the original four-second primitive clip. Seek or change playback speed to show mirrored audience playback. Ending this foreground video automatically advances to the next slide. The audience stays muted. The startup gate prepares every video before any slide appears.', sources=DOCS),

    slide('moge1-results', 'Motion behind the message', [
        t(64, 152, 'Motion behind the message', 58, True),
        t(64, 272, 'A video can be the background', 40, True, color=TEAL),
        t(64, 350, 'A soundtrack can run alongside it', 36),
        t(64, 542, 'Try the music toggle and volume slider', 32, color=MUTED),
    ], video={'src':'media/demo/primitives.mp4', 'poster':'media/demo/motion-poster.png',
              'bounds':[0,0,1152,648], 'background':True, 'dim':.78,
              'autoplay':True, 'muted':True, 'loop':True}, soundtrack=soundtrack,
    notes='The same clip loops behind the text, dimmed for contrast. A quiet locally synthesized chord plays separately. Browser autoplay rules may require Enable music. Adjust volume and mute. The same audio player continues on the next slide.', sources=DOCS),

    slide('moge1-invariance-demo', 'Keep the soundtrack flowing', [
        title('Keep the soundtrack flowing'),
        *lines(64, 176, ['One audio player', 'Across two slides'], 44, True, width=560, leading=70),
        *lines(64, 372, ['This image is a bundled SVG.', 'The next slide stops the music.'], 32, color=MUTED, width=600, leading=56),
    ], images=[picture('media/demo/stage-3.svg', [688,150,400,356],
                       'Original square, circle, and cube made from SVG primitives', fit='cover')], soundtrack=soundtrack,
    notes='Audio does not restart because slides 6 and 7 share one soundtrack source. This slide also embeds a local SVG cropped to fill its bounds. Leave the slide to stop the music. All artwork and audio is original; no third-party music is bundled.', sources=DOCS),

    slide('moge1-representation', 'Drag a point cloud', [
        title('Drag a point cloud'),
        t(64, 576, 'Orbit the cube and sphere, then reset the view', 32, color=MUTED),
    ], scene={'kind':'cloud', 'bounds':[64,124,1024,420], **cloud},
    notes='Drag to orbit deterministic cube and sphere samples. Reset view restores the initial camera. This is toy geometry, not a model reconstruction. The camera persists during navigation and synchronizes with the audience.', sources=DOCS),

    slide('moge1-affine-invariant', 'Compare raw and aligned shapes', [
        title('Compare raw and aligned shapes',50),
        t(64, 576, 'Switch the scale; keep the camera fixed', 32, color=MUTED),
    ], scene={'kind':'cloud', 'bounds':[64,124,1024,420], **cloud,
              'prediction_points':prediction, 'alignment_scale':1.6},
    notes='The pink toy cloud is the reference divided by 1.6. Aligned scale applies the inverse factor so the points coincide. Toggle Raw scale and Aligned scale, then orbit. Framing stays fixed so the visual change comes from scale.', sources=DOCS),

    slide('moge1-normalized-shift', 'Two sliders, one projection', [
        title('Two sliders, one projection'),
        t(64, 580, 'Change scale and shift; compare the two rays', 32, color=MUTED),
    ], scene={'kind':'normalized-shift', 'bounds':[64,124,1024,428]},
    notes='Scaling a point map by s and shifting depth by t has the same projection as unit scale shifted by t/s. Try scale 2.4 and shift 3.6: normalized shift is 1.5. Pink and mint endpoints share camera rays. This is an analytic teaching example.', sources=DOCS),

    slide('moge1-supervision', 'A larger scene, the same image', [
        title('A larger scene, the same image'),
        t(64, 576, 'Move the slider and watch the image stay still', 32, color=MUTED),
    ], scene={'kind':'ambiguity', 'bounds':[48,124,1056,420]},
    notes='Scale the cube around a fixed camera. Size and distance increase together so the pinhole image stays unchanged. This slider scene illustrates a concept without any dataset or model.', sources=DOCS),

    slide('moge1-training', 'Compare before and after', [
        title('Compare before and after'),
        t(64, 124, 'Before', 34, True, color=GOLD, width=340),
        t(424, 124, 'After', 34, True, color=TEAL, width=340),
        *lines(812, 220, ['One correction', 'Two views', 'Shared orbit'], 32, True, width=276, leading=56),
        t(64, 566, 'Drag either panel to rotate both', 32, color=MUTED),
    ], scene={'kind':'correction', 'bounds':[64,180,700,348],
              'ground_truth':cloud['points'], 'prediction':prediction, 'applied_scale':1.6},
    notes='Overlay reference and toy input before and after exact scale correction. Drag either panel to rotate both with the same camera. Reset view restores both. Colors describe toy roles, not model names or accuracy claims.', sources=DOCS),

    slide('moge2-section', 'Browse a sequence beside a still', [
        title('Browse a sequence beside a still',50),
        t(64, 584, 'Play or scrub the right panel; orbit either cloud', 32, color=MUTED),
    ], scene={'kind':'pair', 'bounds':[48,112,1056,450], 'cases':[
        {'label':'Still primitives', 'frames':[dict(sequence[0])],
         'view':{'center':[0,0,0], 'radius':3, 'fit':210, 'projection_center':[0,0]}},
        {'label':'Primitive sequence', 'frames':sequence,
         'view':{'center':[0,0,0], 'radius':3, 'fit':210, 'projection_center':[0,0]}},
    ]}, notes='The left gallery is a still; the right has three toy frames. Play cycles the sequence and the slider scrubs it. Drag each cloud independently. These are procedural primitives, not depth estimation results.', sources=DOCS),

    slide('moge2-video', 'Step through image stages', [
        title('Step through image stages'),
        t(64, 574, 'Use Previous, Next, or the stage slider', 32, color=MUTED),
    ], scene={'kind':'steps', 'bounds':[64,124,1024,420], 'frames':[
        {'image':f'media/demo/stage-{i}.png', 'label':label}
        for i,label in enumerate(['Empty canvas','Add square','Add circle','Add depth'])
    ]}, notes='Browse four locally rendered SVG stages. The generic image-stage viewer can show method iterations, edits, or diagrams. Returning keeps the selected stage. All frames decode before startup completes.', sources=DOCS),

    slide('moge2-results', 'Toy evidence: filter and inspect', [t(64, 20, 'Toy evidence: filter and inspect', 44, True)],
    widget='diode', notes='A synthetic ten-case fixture, not DIODE data or measured results. Try environment and policy presets, the kept/rejected filter, plot points, and the case selector. Tune policy opens settings; Apply policy updates coverage and error from frozen diagnostics. Thresholds filter saved cases rather than refitting live data.', sources=DOCS),

    slide('moge2-scale-problem', 'Toy measurements: pick a dimension', [t(64, 20, 'Toy measurements: pick a dimension', 44, True)],
    widget='real', notes='A synthetic four-measurement, two-scene fixture. Select a scene and dimension. Endpoints, assigned size, unscaled span, and implied scale update together. Dimensions are assigned to drawn shapes, not measured physical objects.', sources=DOCS),

    slide('moge2-architecture', 'Toy results: compare the correction', [t(64, 20, 'Toy results: compare the correction', 44, True)],
    widget='predictions', notes='Compare toy dimensions with an unscaled input and corrected estimate. Scene 0000 uses exact correction and is accepted. Scene 0001 deliberately uses an incorrect factor and is rejected. Rejected results remain inspectable. These values are fixture arithmetic, not model evaluation.', sources=DOCS),

    slide('moge2-data-refinement', 'Your notes, their slides', [
        title('Your notes, their slides'),
        t(64, 174, 'Presenter', 44, True, color=TEAL, width=450),
        *lines(64, 266, ['Private notes + prompts', 'Autosave in this browser', 'Export a notes backup'], 34, width=480, leading=62),
        t(624, 174, 'Audience', 44, True, color=PINK, width=450),
        *lines(624, 266, ['A clean slide window', 'Synced demos + playback', 'No presenter notes'], 34, width=464, leading=62),
        t(64, 552, 'Open Audience window, then try a demo', 32, color=MUTED),
    ], notes='Open Audience window. Enter a note, navigate away, and return. Notes autosave locally by deck and slide ID. Export all notes downloads Markdown including notes for removed slides. Audience state includes slides, builds, focus, video, and demos; no note text is sent.', sources=DOCS),

    slide('moge2-training', 'Present at your own pace', [
        title('Present at your own pace'),
        t(64, 170, 'Arrow keys   Navigate slides and build steps', 36),
        t(64, 250, 'G            Overview and jump to a slide', 36),
        t(64, 330, 'F / N       Fullscreen or toggle notes', 36),
        t(64, 432, 'Which demo should we try again?', 40, True, color=GOLD),
        t(64, 554, 'Click the question to highlight it', 32, color=MUTED),
    ], notes='Show overview with G, close with Escape. Help lists numeric jumps 1–9; Home and End also work. Click the question to highlight and again to clear it. Highlights synchronize with the audience. Typing in notes and manipulating controls do not trigger slide shortcuts.', sources=DOCS),

    slide('moge3-section', 'Sources are one click away', [
        title('Sources are one click away'),
        t(64, 176, 'Open Sources in the top bar', 42, True, color=TEAL),
        *lines(64, 284, ['Read the context behind this slide.', 'Follow links to code and documentation.', 'Keep citations beside the material they explain.'], 34, leading=64),
        t(64, 546, 'The bundled demos need no external requests', 32, color=MUTED),
    ], notes='Sources shows slide context and clickable links. External links open separately and require a connection. The demos and fixtures are bundled locally. Artwork and data provenance is recorded in references/SOURCES.md.',
    sources=[('JostSlides repository',REPO), ('Authoring guide',REPO+'/blob/main/docs/AUTHORING.md'),
             ('Runtime architecture',REPO+'/blob/main/docs/ARCHITECTURE.md')]),

    slide('moge3-method', 'Write Python, share a deck', [
        title('Write Python, share a deck'),
        t(64, 160, 'Author', 40, True, color=TEAL, width=450),
        *lines(64, 242, ['Edit deck.py', 'Check text and assets', 'Build the local preview'], 34, width=460, leading=60),
        t(624, 160, 'Share', 40, True, color=PINK, width=450),
        *lines(624, 242, ['Portable HTML + media', 'PDF with demo snapshots', 'Editable PPTX + movies'], 34, width=464, leading=60),
        t(64, 502, 'python slides.py check', 32, color=GOLD),
        t(64, 554, 'python slides.py export', 32, color=GOLD),
    ], notes='Edit deck.py; run python slides.py check and python slides.py build. Export writes PDF, PPTX, speaker prompts, previews, and demo snapshots under build/2026-09-24/. HTML keeps live demos. PDF/PPTX use stills for interactions. PPTX text and rectangles stay editable and movies are embedded. Create a new deck with python slides.py new YYYY-MM-DD --title "Talk title". Historical IDs remain for note continuity.', sources=DOCS),

    slide('discussion', 'Make the next deck yours', [
        t(64, 136, 'Make the next deck yours', 64, True),
        t(64, 274, 'Keep the style. Replace the primitives.', 40, True, color=TEAL),
        *lines(64, 394, ['Start with this example or the new-deck scaffold.', 'Add your own evidence, media, and speaker notes.'], 32, color=MUTED, leading=58),
        t(64, 560, 'What would you make interactive?', 36, True, color=GOLD),
    ], notes='Closing prompt. This tour covers automatic motion, builds and details, primitives, SVG imagery, foreground/background video, automatic video advance, continuous sound, all six scene types and all three evidence widgets, sources, notes, audience sync, focus, overview, fullscreen, keyboard navigation, validation, and export. The README feature index links every example.', sources=DOCS),
]
