"""Reproduce the showcase's primitive artwork, toy data, video, and audio locally.

Requires the optional Playwright dependency, Chromium, and ffmpeg. Normal deck
builds use the committed outputs and do not need this script or ffmpeg.
"""
import base64
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'media' / 'demo'
EVIDENCE = ROOT / 'evidence'


def cloud(yaw=0):
    points, colors = [], []
    # A cube shell, a sphere, and a horizontal plane: toy geometry, no model.
    for face in range(6):
        for i in range(15):
            for j in range(15):
                p = [(i / 14 - .5) * 1.5, (j / 14 - .5) * 1.5]
                axis, side = face // 2, (-.75 if face % 2 else .75)
                p.insert(axis, side)
                points.append([p[0] - 1.1, p[1], p[2]])
                colors.append([184, 227, 209])
    for i in range(24):
        for j in range(36):
            a, b = i / 23 * math.pi, j / 36 * 2 * math.pi
            points.append([1.1 + .85 * math.sin(a) * math.cos(b),
                           .85 * math.cos(a), .85 * math.sin(a) * math.sin(b)])
            colors.append([236, 147, 215])
    for i in range(36):
        for j in range(15):
            points.append([(i / 35 - .5) * 4.4, -.9, (j / 14 - .5) * 2.4])
            colors.append([140, 184, 255])
    c, s = math.cos(yaw), math.sin(yaw)
    points = [[round(x*c-z*s, 5), round(y, 5), round(x*s+z*c, 5)] for x,y,z in points]
    return {'points': points, 'colors': colors}


def svg(stage=3, variant=0):
    colors = ['#b8e3d1', '#ebcb8b', '#ec93d7', '#8cb8ff']
    # Deliberately simple, inspectable native SVG primitives.
    shapes = ['<rect x="0" y="0" width="1024" height="768" fill="#080c10"/>']
    if stage >= 1:
        shapes += [f'<rect x="190" y="250" width="280" height="280" rx="0" fill="{colors[variant%4]}"/>']
    if stage >= 2:
        shapes += [f'<circle cx="690" cy="390" r="145" fill="{colors[(variant+2)%4]}"/>']
    if stage >= 3:
        shapes += ['<path d="M190 530L280 610H560L470 530Z" fill="#42776d"/>',
                   '<path d="M470 250L560 330V610L470 530Z" fill="#6da993"/>',
                   '<path d="M190 250L280 330H560L470 250Z" fill="#d5f5e8"/>',
                   '<line x1="96" y1="665" x2="928" y2="665" stroke="#8cb8ff" stroke-width="5"/>']
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="768" viewBox="0 0 1024 768">' + ''.join(shapes) + '</svg>'


ANIMATION = """<!doctype html><style>body{margin:0;background:#000}</style>
<canvas width="1152" height="648"></canvas><script>
const c=document.querySelector('canvas'),ctx=c.getContext('2d');
window.paint=(frame)=>{
 const phase=frame/96*Math.PI*2;ctx.fillStyle='#000';ctx.fillRect(0,0,1152,648);
 ctx.strokeStyle='#242424';ctx.lineWidth=2;
 for(let x=64;x<1152;x+=64){ctx.beginPath();ctx.moveTo(x,96);ctx.lineTo(x,552);ctx.stroke();}
 for(let y=96;y<=552;y+=64){ctx.beginPath();ctx.moveTo(64,y);ctx.lineTo(1088,y);ctx.stroke();}
 ctx.fillStyle='#b8e3d1';ctx.beginPath();ctx.arc(310,324+Math.sin(phase)*100,85,0,Math.PI*2);ctx.fill();
 ctx.save();ctx.translate(576,324);ctx.rotate(phase);ctx.fillStyle='#ebcb8b';ctx.fillRect(-76,-76,152,152);ctx.restore();
 ctx.save();ctx.translate(850,324+Math.cos(phase)*80);ctx.rotate(-phase*.5);ctx.fillStyle='#ec93d7';
 ctx.beginPath();ctx.moveTo(0,-98);ctx.lineTo(90,70);ctx.lineTo(-90,70);ctx.closePath();ctx.fill();ctx.restore();
};paint(0);</script>"""


def main():
    if not shutil.which('ffmpeg'):
        raise SystemExit('Install ffmpeg to reproduce the demo video and audio')
    MEDIA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as temporary:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width':1024,'height':768})
        for stage in range(4):
            source = MEDIA / f'stage-{stage}.svg'
            source.write_text(svg(stage))
            page.goto(source.as_uri())
            page.locator('svg').screenshot(path=str(MEDIA / f'stage-{stage}.png'))
        for variant in range(3):
            page.goto('about:blank')
            page.set_content(svg(3, variant))
            page.locator('svg').screenshot(path=str(MEDIA / f'objects-{variant}.jpg'), type='jpeg', quality=90)
        page.set_viewport_size({'width':1152,'height':648})
        page.set_content(ANIMATION)
        page.locator('canvas').screenshot(path=str(MEDIA / 'motion-poster.png'))
        for frame in range(96):
            page.evaluate('paint', frame)
            page.locator('canvas').screenshot(path=str(Path(temporary) / f'{frame:04}.png'))
        browser.close()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24',
                        '-i', str(Path(temporary) / '%04d.png'), '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart',
                        str(MEDIA / 'primitives.mp4')], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i',
                    'aevalsrc=0.035*(sin(2*PI*220*t)+sin(2*PI*275*t)+sin(2*PI*330*t)):s=44100:d=8',
                    '-af', 'afade=t=in:d=0.5,afade=t=out:st=7.5:d=0.5',
                    '-c:a', 'pcm_s16le', str(MEDIA / 'chord.wav')], check=True)
    geometry = cloud()
    (EVIDENCE / 'primitive-cloud.json').write_text(json.dumps(geometry, separators=(',',':')))
    frames = [dict(image=f'media/demo/objects-{i%3}.jpg', **cloud(i*.12)) for i in range(3)]
    (EVIDENCE / 'primitive-sequence.json').write_text(json.dumps(frames, separators=(',',':')))

    def image(variant):
        return 'data:image/jpeg;base64,' + base64.b64encode((MEDIA / f'objects-{variant}.jpg').read_bytes()).decode()

    ratios = [1.075, 1.25, 1.4, 1.5, 1.75]
    cases = []
    for i in range(10):
        metrics = []
        for ratio in ratios:
            error = round(1 + i * 1.8 + (ratio-1)*4, 2)
            metrics.append(dict(global_ratio=ratio, success=i != 9, error_pct=error,
                                case_residual_pct=1 + i*.8, supporting_anchors=6-i//2))
        cases.append(dict(case=f'toy-{i+1:02}', environment='indoor' if i<5 else 'outdoor',
                          before_objects=8-i//2, image=image(i%3), metrics=metrics))
    scenes, results = [], []
    for i in range(2):
        measurements = []
        for j, (label, a, b, cm) in enumerate([
            ('Square width', [190,250], [470,250], 28),
            ('Circle diameter', [545,390], [835,390], 29),
        ]):
            scale = 1.4 + i*.2
            unscaled_m = cm/100/scale
            measurements.append(dict(id=f'dimension-{j}', label=label, frame_index=0,
                                     pixel_a=a, pixel_b=b, gt_input=f'{cm} cm (toy)',
                                     unscaled_m=unscaled_m, implied_scale=scale))
            correction = scale if i == 0 else 1.2
            estimate = cm/scale*correction
            results.append(dict(scene=f'{i:04}', annotation_id=f'dimension-{j}',
                                accepted=i==0, ground_truth_cm=cm, unscaled_cm=cm/scale,
                                estimated_cm=estimate, scale=correction,
                                unscaled_absolute_relative_error_pct=abs(1/scale-1)*100,
                                absolute_relative_error_pct=abs(estimate/cm-1)*100))
        scenes.append(dict(scene=f'{i:04}', images=[image(i)], measurements=measurements))
    snapshot = dict(diode=dict(ratios=ratios, cases=cases), real=scenes,
                    real_results=dict(measurements=results))
    (EVIDENCE / 'toy-evidence.json').write_text(json.dumps(snapshot, separators=(',',':')))
    print('Rebuilt original primitive artwork, 4-second video, 8-second chord, and toy evidence')


if __name__ == '__main__':
    main()
