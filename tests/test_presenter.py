"""Browser regression checks for the public feature tour and multiple examples."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

from playwright.sync_api import sync_playwright, expect
from slidekit.project import ROOT, load_deck
from slidekit.build import build


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class PresenterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = load_deck()
        cls.page_path = build(cls.deck, activate=False)
        build(load_deck('2026-10-02'), activate=False)
        cls.ids = [s['id'] for s in cls.deck.slides]
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(offline=True, viewport={'width':1600,'height':1000})
        self.page = self.context.new_page()
        self.errors, self.requests = [], []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.context.on('request', lambda r: self.requests.append(r.url))
        self.page.goto(self.page_path.as_uri())
        self.page.wait_for_function('presentationReady', timeout=30000)

    def tearDown(self):
        try:
            self.assertFalse(self.errors, self.errors)
        finally:
            self.context.close()

    def go(self, identity):
        self.page.evaluate('i=>go(i)', self.ids.index(identity))

    def slider(self, name, value):
        self.page.locator(f'input[aria-label="{name}"]').evaluate(
            '(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}', str(value))

    def test_offline_startup_and_all_slides(self):
        expect(self.page.locator('#counter')).to_have_text('1 / 22')
        self.assertTrue(self.page.evaluate('startupFontsReady && [...startupImages.values()].every(x=>x.ready)'))
        self.assertTrue(self.page.evaluate('[...videoPool.values(),...soundtrackPool.values()].every(x=>x.ready)'))
        for identity in self.ids:
            self.go(identity)
            self.assertTrue(self.page.evaluate('[...document.querySelectorAll("#slide img")].every(i=>i.complete&&i.naturalWidth>0)'))
        self.assertTrue(all(u.startswith(('file:', 'data:', 'blob:')) for u in self.requests), self.requests)

    def test_motion_builds_and_detail(self):
        self.page.evaluate('go(1)')
        expect(self.page.locator('.motion-overlay')).to_have_count(1)
        expect(self.page.locator('.motion-overlay')).to_have_count(0, timeout=4000)
        self.go('moge1-ambiguity')
        self.assertEqual(self.page.locator('#slide [data-build="2"]:visible').count(), 0)
        self.page.locator('#build-play').click()
        self.page.wait_for_function('buildStep===2&&!buildPlaying', timeout=10000)
        self.assertGreater(self.page.locator('#slide [data-build="2"]:visible').count(), 0)
        self.page.locator('#build-explore').click()
        expect(self.page.locator('#slide')).to_have_class('slide pipeline-detail')
        self.page.keyboard.press('Escape')
        self.assertFalse(self.page.evaluate('buildDetail'))
        self.page.locator('#build-replay').click()
        self.assertEqual(self.page.evaluate('buildStep'), 0)

    def test_all_scene_controls_and_shift_extremes(self):
        self.go('moge1-representation')
        canvas = self.page.locator('#slide canvas')
        box = canvas.bounding_box()
        self.page.mouse.move(box['x']+150,box['y']+100)
        self.page.mouse.down();self.page.mouse.move(box['x']+220,box['y']+130);self.page.mouse.up()
        self.assertNotEqual(self.page.evaluate('widgetState.scenes[SLIDES[current].id+"-scene"].yaw'), -.18)
        self.page.get_by_role('button', name='Reset view', exact=True).click()
        self.assertEqual(self.page.evaluate('widgetState.scenes[SLIDES[current].id+"-scene"].yaw'), -.18)
        self.go('moge1-affine-invariant')
        self.page.get_by_role('button',name='Aligned scale',exact=True).click()
        expect(self.page.locator('.scene-view')).to_have_attribute('data-aligned','true')
        self.go('moge1-normalized-shift')
        self.slider('Affine point-map scale',2.4);self.slider('Affine point-map depth shift',3.6)
        scene = self.page.locator('.normalized-shift-scene')
        expect(scene).to_have_attribute('data-normalized-shift','1.500')
        self.assertLess(float(scene.get_attribute('data-projection-error')),1e-12)
        for scale in [.5,2.5]:
            for shift in [0,4]:
                self.slider('Affine point-map scale',scale);self.slider('Affine point-map depth shift',shift)
                self.assertLess(float(scene.get_attribute('data-projection-error')),1e-12)
        # Controls and caption must remain inside the scene at the maximum values.
        self.assertTrue(scene.evaluate('(e)=>[...e.querySelectorAll("label,output,input")].every(c=>{const a=c.getBoundingClientRect(),b=e.getBoundingClientRect();return a.left>=b.left&&a.right<=b.right+1&&a.bottom<=b.bottom+1})'))
        self.go('moge1-supervision');self.slider('Scene size around a fixed camera',3)
        self.assertLess(float(self.page.locator('.scene-view').get_attribute('data-projection-error')),1e-12)
        self.go('moge1-training')
        expect(self.page.locator('.correction-cloud')).to_have_count(2)
        self.assertIn('Reference',self.page.locator('.correction-controls').inner_text())
        self.go('moge2-section');self.slider('Sequence frame',2)
        expect(self.page.locator('.pair-scene')).to_have_attribute('data-frame','2')
        self.page.get_by_role('button',name='Play',exact=True).click()
        self.page.wait_for_function('document.querySelector(".pair-scene").dataset.frame!=="2"')
        self.page.get_by_role('button',name='Pause',exact=True).click()
        self.go('moge2-video');self.slider('Refinement step',3)
        expect(self.page.locator('.steps-label')).to_have_text('Add depth')
        expect(self.page.locator('.steps-image')).to_have_attribute('alt','Add depth')
        self.go('moge1-supervision');self.go('moge2-video')
        expect(self.page.locator('.steps-scene')).to_have_attribute('data-step','3')

    def test_evidence_filters_and_results(self):
        self.go('moge2-results')
        expect(self.page.locator('#diode-coverage')).to_have_text('7 / 10')
        self.page.locator('#diode-env').select_option('outdoor')
        expect(self.page.locator('#diode-coverage')).to_have_text('2 / 5')
        self.page.locator('#diode-show').select_option('rejected')
        self.assertEqual(self.page.locator('.case-point').count(),2)
        self.page.locator('#policy-settings').click()
        self.page.locator('[data-param="2"]').select_option('off')
        self.page.locator('#apply-policy').click()
        expect(self.page.locator('#diode-policy')).to_have_value('custom')
        expect(self.page.locator('#diode-coverage')).to_have_text('3 / 5')
        self.go('moge2-scale-problem')
        self.assertIn('4 measurements / 2 scenes',self.page.locator('.evidence-controls').inner_text())
        self.page.locator('#real-measurement').select_option('1')
        self.assertIn('29 cm (toy)', self.page.locator('.real-explainer').inner_text())
        self.go('moge2-architecture');self.page.locator('#prediction-scene').select_option('0001')
        self.assertIn('Rejected',self.page.locator('#prediction-status').inner_text())
        expect(self.page.locator('#prediction-error')).to_have_text('25.00%')

    def test_dropdown_mouse_keyboard_and_policy_dialog(self):
        self.go('moge2-results')
        field = self.page.get_by_role('combobox',name='Evidence environment',exact=True)
        field.click()
        expect(self.page.get_by_role('listbox',name='Evidence environment',exact=True)).to_be_visible()
        self.page.get_by_role('option',name='Outdoor',exact=True).click()
        expect(self.page.locator('#diode-coverage')).to_have_text('2 / 5')
        expect(field).to_have_attribute('aria-expanded','false')
        # Arrow keys belong to the dropdown, not to presentation navigation.
        field.press('Enter');field.press('Home');field.press('Enter')
        expect(self.page.locator('#diode-env')).to_have_value('all')
        expect(self.page.locator('#counter')).to_have_text('15 / 22')
        field.press('ArrowDown');field.press('Escape')
        expect(self.page.locator('#diode-env')).to_have_value('all')
        expect(self.page.get_by_role('listbox')).to_have_count(0)
        field.press('o');field.press('Enter')
        expect(self.page.locator('#diode-env')).to_have_value('outdoor')
        self.page.locator('#policy-settings').click()
        threshold = self.page.get_by_role('combobox',name='Maximum residual (%)',exact=True)
        threshold.click();self.page.keyboard.press('Escape')
        expect(self.page.locator('#evidence-dialog')).to_be_visible()
        threshold.click();self.page.get_by_role('option',name='off',exact=True).click()
        self.page.locator('#apply-policy').click()
        expect(self.page.locator('#diode-coverage')).to_have_text('3 / 5')
        self.page.get_by_role('combobox',name='Evidence environment',exact=True).click()
        self.page.locator('#next').click()
        expect(self.page.get_by_role('listbox')).to_have_count(0)

    def test_orbit_viewers_keep_geometry_upright_and_follow_vertical_drag(self):
        # Known landmarks distinguish world orientation from the pointer convention.
        # Record actual canvas draws rather than merely checking a pitch formula.
        self.page.evaluate('''() => {
            const draw = CanvasRenderingContext2D.prototype.fillRect;
            CanvasRenderingContext2D.prototype.fillRect = function(x,y,w,h) {
                this.canvas.landmarks ??= [];
                if (w < 10) this.canvas.landmarks.push({x,y,color:this.fillStyle});
                else this.canvas.landmarks = [];
                return draw.call(this,x,y,w,h);
            };
        }''')
        for identity, kind in [('moge1-representation','cloud'),
                               ('moge1-training','correction'),
                               ('moge2-section','pair')]:
            with self.subTest(kind=kind):
                self.page.evaluate('''({index,kind}) => {
                    const points = [[0,1,0],[0,-1,0],[0,0,-1],[0,0,1],[1,0,0],[-1,0,0]];
                    const colors = [[255,0,0],[0,0,255],[255,255,255],[255,255,0],[255,0,255],[0,255,255]];
                    const s = SLIDES[index].scene;
                    s.initial_yaw = 0; s.initial_pitch = 0;
                    delete widgetState.scenes?.[SLIDES[index].id+'-scene'];
                    if (kind==='cloud') Object.assign(s,{points,colors});
                    if (kind==='correction') Object.assign(s,{ground_truth:points,prediction:points,applied_scale:1});
                    if (kind==='pair') for (const c of s.cases) {
                        c.view={center:[0,0,0],radius:1,fit:90,projection_center:[0,0]};
                        for (const frame of c.frames) Object.assign(frame,{points,colors});
                    }
                    go(index);
                }''', {'index':self.ids.index(identity),'kind':kind})
                canvases = self.page.locator('#slide canvas')
                for panel in range(canvases.count()):
                    canvas = canvases.nth(panel)
                    marks = canvas.evaluate('c=>c.landmarks')
                    if kind == 'correction':
                        # At zero rotation, stable depth sorting draws the +Y
                        # reference landmark before the -Y reference landmark.
                        reference = [p for p in marks if p['color']=='#80dad6']
                        self.assertLess(reference[1]['y'], reference[2]['y'])
                    else:
                        top = next(p for p in marks if p['color']=='#ff0000')
                        bottom = next(p for p in marks if p['color']=='#0000ff')
                        self.assertLess(top['y'],bottom['y'])
                    box = canvas.bounding_box()
                    self.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
                    self.page.mouse.down()
                    self.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2+24)
                    self.page.mouse.up()
                    state = self.page.evaluate('widgetState.scenes[SLIDES[current].id+"-scene"]')
                    pitch = state['pitch'][panel] if kind=='pair' else state['pitch']
                    self.assertLess(pitch,0)
                    if kind != 'correction':
                        before = next(p for p in marks if p['color']=='#ffffff')
                        after = next(p for p in canvas.evaluate('c=>c.landmarks') if p['color']=='#ffffff')
                        self.assertGreater(after['y'],before['y'])
                    else:
                        after = [p for p in canvas.evaluate('c=>c.landmarks') if p['color']=='#80dad6']
                        self.assertGreater(after[-1]['y'],reference[-1]['y'])
                    # Dragging back up restores the camera, for either panel.
                    self.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2+24)
                    self.page.mouse.down()
                    self.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
                    self.page.mouse.up()
                    state = self.page.evaluate('widgetState.scenes[SLIDES[current].id+"-scene"]')
                    pitch = state['pitch'][panel] if kind=='pair' else state['pitch']
                    self.assertAlmostEqual(pitch,0)

    def test_video_advance_and_continuous_soundtrack(self):
        self.go('moge1-video')
        self.page.evaluate('document.querySelector("#slide video").play()')
        self.page.wait_for_function('SLIDES[current].id==="moge1-results"',timeout=10000)
        self.assertTrue(self.page.locator('#slide video').evaluate('v=>v.loop&&v.muted'))
        self.page.evaluate('window.savedSoundtrack=activeSoundtrack;activeSoundtrack.audio.currentTime=2')
        self.go('moge1-invariance-demo')
        self.assertTrue(self.page.evaluate('activeSoundtrack===window.savedSoundtrack&&activeSoundtrack.audio.currentTime>=2'))
        self.page.locator('#music-volume').evaluate('(e)=>{e.value="20";e.dispatchEvent(new Event("input",{bubbles:true}))}')
        self.assertAlmostEqual(self.page.evaluate('activeSoundtrack.audio.volume'),.2)
        self.go('moge1-representation')
        self.assertTrue(self.page.evaluate('activeSoundtrack===null&&window.savedSoundtrack.audio.paused'))

    def test_notes_sources_overview_and_audience(self):
        self.go('moge2-data-refinement')
        self.page.locator('#notes-input').fill('Private test note')
        self.page.reload();self.page.wait_for_function('presentationReady')
        expect(self.page.locator('#notes-input')).to_have_value('Private test note')
        with self.page.expect_popup() as popup:
            self.page.locator('#audience-open').click()
        audience = popup.value;audience.wait_for_function('presentationReady')
        expect(audience.locator('.notes')).not_to_be_visible()
        self.go('moge1-normalized-shift');self.slider('Affine point-map scale',2.4)
        expect(audience.locator('.normalized-shift-scene')).to_have_attribute('data-scale','2.4')
        self.assertTrue(audience.evaluate('document.querySelector("#notes-input").value===""'))
        self.go('moge2-training')
        self.page.get_by_role('button',name='Which demo should we try again?',exact=True).click()
        expect(audience.locator('.focused')).to_have_count(1)
        self.page.keyboard.press('g')
        expect(self.page.locator('#overview-grid .thumb')).to_have_count(22)
        self.page.keyboard.press('Escape')
        self.go('moge3-section');self.page.locator('#sources').click()
        expect(self.page.locator('#evidence-dialog a')).to_have_count(3)
        expect(self.page.get_by_role('link',name='Authoring guide ↗')).to_have_attribute('target','_blank')
        self.page.keyboard.press('Escape')
        self.page.evaluate('notes["removed-example-slide"]="Archived note"')
        with self.page.expect_download() as download:
            self.page.locator('#export-notes').click()
        body = Path(download.value.path()).read_text()
        self.assertIn('Private test note',body);self.assertIn('Archived note',body)

    def test_gate_failure_retry_and_deck_picker(self):
        self.context.set_offline(False)
        self.page.route('**/primitives.mp4',lambda route:route.abort())
        self.page.goto(self.origin+'/build/2026-09-24/index.html')
        expect(self.page.locator('#startup-screen')).to_have_attribute('data-state','error')
        self.assertFalse(self.page.evaluate('presentationReady'))
        self.assertEqual(self.page.locator('#slide > *').count(),0)
        self.page.evaluate('go(3)');self.page.keyboard.press('ArrowRight')
        self.assertEqual(self.page.evaluate('current'),0)
        self.page.unroute('**/primitives.mp4')
        self.page.locator('#startup-retry').click();self.page.wait_for_function('presentationReady')
        self.page.locator('#notes-input').fill('Showcase note')
        expect(self.page.locator('#header-deck-menu')).to_be_visible()
        self.page.locator('#header-deck-menu summary').click()
        self.page.locator('#header-deck-menu .deck-option').filter(has_text='A tiny talk').click()
        self.page.wait_for_function('presentationReady&&META.title==="A tiny talk"')
        expect(self.page.locator('#notes-input')).to_have_value('')
        self.page.locator('#notes-input').fill('Starter note')
        self.page.locator('#header-deck-menu summary').click()
        self.page.locator('#header-deck-menu .deck-option').filter(has_text='JostSlides').click()
        self.page.wait_for_function('presentationReady&&META.title.startsWith("JostSlides")')
        expect(self.page.locator('#notes-input')).to_have_value('Showcase note')


if __name__ == '__main__':
    unittest.main()
