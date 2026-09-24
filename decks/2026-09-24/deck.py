"""Group presentation on the MoGe paper series."""
from pathlib import Path
import json

from slidekit.dark import t, lines, slide, MUTED, ACCENT, PANEL


META = {
    'id': 'accidental-size-probes-2026-09-24',
    'title': 'Fantastic MoGEs and Where to Find Them',
    'date': '2026-09-24',
    'date_label': 'September 24, 2026',
    'show_date': False,
    'export_stem': 'moge-series-2026-09-24',
    'theme': 'black',
    'font': 'Jost',
    'motion': 'remotion',
}
EVIDENCE = {}

ROOT = Path(__file__).parent
M1_PAPER = 'https://arxiv.org/abs/2410.19115'
M1_PAGE = 'https://wangrc.site/MoGePage/'
M2_PAPER = 'https://proceedings.neurips.cc/paper_files/paper/2025/hash/336572db3e99930814d6b328d4220cb6-Abstract-Conference.html'
M2_PAGE = 'https://wangrc.site/MoGe2Page/'
M3_PAPER = 'https://arxiv.org/abs/2607.17967'
M3_PAGE = 'https://qft-333.github.io/moge3page/'
CODE = 'https://github.com/microsoft/MoGe'

TEAL = ACCENT
GOLD = 'EBCB8B'
PINK = 'EC93D7'
BLUE = '8CB8FF'
RED = 'D39494'


def img(src, bounds, alt, **extra):
    return {'src': src, 'bounds': bounds, 'alt': alt, **extra}


def section(identity, name, claim, color):
    return slide(identity, name, [
        t(64, 166, name, 76, True, color=color),
        t(64, 300, claim, 44, True, width=1010),
        t(64, 515, 'Evidence  →  problem  →  method  →  training lesson', 34, color=MUTED),
    ], notes=f'Section transition. The takeaway is: {claim}')


def card(x, y, w, h, title, body, color=TEAL):
    return ([
        t(x + 28, y + 24, title, 34, True, color=color, width=w - 56),
        *lines(x + 28, y + 88, body, 30, width=w - 56, leading=45),
    ], [(x, y, w, h, PANEL)])


def metric_card(x, label, before, after, color=TEAL, direction='↓'):
    text = [
        t(x + 16, 206, label, 30, True, color=MUTED, width=286),
        t(x + 16, 298, before, 34, width=286),
        t(x + 16, 358, direction, 36, True, color=color, width=286),
        t(x + 16, 416, after, 38, True, color=color, width=286),
    ]
    return text, [(x, 184, 318, 336, PANEL)]


moge1_cloud = json.loads((ROOT / 'evidence/moge1-office-cloud.json').read_text())
moge2_cloud = json.loads((ROOT / 'evidence/moge2-room-cloud.json').read_text())
moge3_steps = [
    {'image': f'media/moge3/normal-step{i}.png',
     'label': 'Base model' if i == 0 else f'Refinement {i}'}
    for i in range(6)
]


SLIDES = []

SLIDES.append(slide('recap', 'Fantastic MoGEs and Where to Find Them', [
    *lines(64, 172, ['Fantastic MoGEs', 'and Where to Find Them'], 52, True, width=650, leading=66),
    t(64, 374, 'Guangzhao He', 40),
    t(64, 440, 'September 24, 2026', 32, color=MUTED),
], images=[img('media/moge-title-hero.png', [0, 0, 1152, 648], 'Three fantastic forms emerging from point clouds and sparse voxels', fit='cover')],
notes='Title slide. Guangzhao He. September 24, 2026. The original title artwork was generated for this deck and visualizes the three MoGe generations as fantastic forms emerging from point clouds, voxel shells and layered geometry.',
sources=[('MoGe 1 paper', M1_PAPER), ('MoGe 2 paper', M2_PAPER), ('MoGe 3 paper', M3_PAPER)]))

text = [t(64, 50, 'Three papers remove three bottlenecks', 54, True)]
rects = []
for x, name, year, claim, color in [
    (64, 'MoGe 1', 'CVPR 2025 oral', 'Ambiguous\nsupervision', TEAL),
    (412, 'MoGe 2', 'NeurIPS 2025', 'Metric scale +\nnoisy labels', GOLD),
    (760, 'MoGe 3', 'arXiv 2026', 'Fine 3D\nstructure', PINK),
]:
    rects.append((x, 170, 304, 330, PANEL))
    text += [t(x + 26, 198, name, 46, True, color=color, width=252),
             t(x + 26, 266, year, 30, color=MUTED, width=252)]
    text += lines(x + 26, 342, claim.split('\n'), 38, True, width=252, leading=50)
text += [t(64, 552, 'The architecture evolves after supervision and data problems are exposed', 32, color=MUTED)]
SLIDES.append(slide('series-map', 'Three papers remove three bottlenecks', text, rects,
notes='Roadmap. MoGe 1 was submitted in 2024 and appeared as a CVPR 2025 oral. MoGe 2 appeared at NeurIPS 2025. MoGe 3 was released on arXiv in July 2026. This slide states the interpretation used for the talk; it does not imply the papers are the only work addressing these bottlenecks.',
sources=[('MoGe project and publication list', CODE)]))


# MoGe 1
SLIDES.append(section('moge1-section', 'MoGe 1', 'Make the supervision match the ambiguity', TEAL))

left_text, left_rect = card(64, 176, 480, 340, 'What the model sees', ['Similar appearance', 'Same relative shape', 'Likely the same prediction'], TEAL)
right_text, right_rect = card(608, 176, 480, 340, 'What labels contain', ['Different focal lengths', 'Different camera distances', 'Different XYZ coordinates'], RED)
SLIDES.append(slide('moge1-ambiguity', 'Direct XYZ loss learns the camera setup',
    [t(64, 54, 'Direct XYZ loss learns the camera setup', 52, True)] + left_text + right_text +
    [t(64, 560, 'The labels disagree even when the scene shape agrees', 34, True, color=GOLD, width=1024)],
    left_rect + right_rect,
    notes='Motivation for the affine-invariant design. Similar-looking images can be captured with different focal lengths and camera-to-scene distances. A monocular model is likely to infer similar relative geometry, while the camera-space XYZ labels differ by global scale and translation. A direct point-map loss would therefore punish a sensible prediction with conflicting supervision. MoGe 1 removes the camera choices the image cannot determine before computing the loss.',
    sources=[('MoGe 1, Sections 1 and 3.1', M1_PAPER)]))

predict_text, predict_rect = card(48, 174, 320, 240, '1  Predict', [
    'One XYZ point',
    'for every pixel',
], TEAL)
align_text, align_rect = card(416, 174, 320, 240, '2  Best fit', [
    'One global scale',
    'One depth shift',
], GOLD)
loss_text, loss_rect = card(784, 174, 320, 240, '3  Compute loss', [
    'Aligned map',
    'with ground truth',
], PINK)
SLIDES.append(slide('moge1-affine-invariant', 'Align before computing the loss', [
    t(64, 44, 'Align before computing the loss', 54, True),
    *predict_text, *align_text, *loss_text,
    t(374, 268, '→', 42, True, color=MUTED, width=42),
    t(742, 268, '→', 42, True, color=MUTED, width=42),
    t(64, 456, 'Fit one scale and one depth shift before measuring error', 36, True, color=TEAL, width=1024),
    t(64, 526, 'The remaining error measures the scene shape', 34, True, width=1024),
    t(64, 576, 'MoGe predicts XYZ points, not only depth', 30, color=MUTED, width=1024),
], predict_rect + align_rect + loss_rect,
notes='Plain-language definition of MoGe 1’s affine-invariant point-map loss. Yes: the network predicts one XYZ point per pixel; before comparing the prediction with ground truth, the ROE solver finds one global scale and one shared translation that best align the complete point map; the geometry loss is then computed on the aligned points. Under the paper’s centered-principal-point and square-pixel assumptions, translation simplifies to a shift along the camera z axis. “Invariant” means the training loss does not change when the raw prediction differs only by this global scale and shift. It does not mean a general affine transform with rotation, shear or nonuniform scaling. At inference, focal length and normalized z shift can be recovered, but monocular metric scale remains unknown.',
sources=[('MoGe 1, Section 3.1 and Figure 4', M1_PAPER)]))

SLIDES.append(slide('moge1-invariance-demo', 'Camera setup changes the XYZ labels', [
    t(64, 44, 'Camera setup changes the XYZ labels', 50, True),
    t(64, 458, 'Same scene shape, different focal length and camera distance', 32, True, width=1024),
    t(64, 514, 'Direct XYZ loss treats those camera changes as geometry errors', 34, True, color=RED, width=1024),
    t(64, 570, 'MoGe aligns scale and depth shift before measuring shape', 32, True, color=TEAL, width=1024),
], images=[img('media/moge1/focal-distance-ambiguity.png', [64, 116, 1024, 306], 'MoGe 1 Figure 4 showing focal-distance ambiguity and consistent affine-invariant supervision', fit='contain')],
notes='Official MoGe 1 Figure 4, cropped from the bundled paper without redrawing. Panel (a) shows similar images and similar model predictions paired with ground-truth cameras at different focal lengths and distances. Panel (b) shows that scale-only alignment leaves inconsistent targets. Panel (c) shows that adding translation lets the same predicted geometry align consistently. The figure motivates affine-invariant point-map supervision; it does not claim invariance to arbitrary FOV changes.',
sources=[('MoGe 1, Section 3.1 and Figure 4', M1_PAPER)]))

SLIDES.append(slide('moge1-representation', 'Reprojection fits focal length and depth shift', [
    t(64, 44, 'Reprojection fits focal length and depth shift', 48, True),
    t(64, 334, '1', 40, True, color=TEAL), t(118, 340, 'Each predicted XYZ point came from a known pixel', 34, True, width=930),
    t(64, 406, '2', 40, True, color=GOLD), t(118, 412, 'Try one focal length and one shared depth shift', 34, True, width=930),
    t(64, 478, '3', 40, True, color=PINK), t(118, 484, 'Choose the pair that reprojects closest to those pixels', 34, True, width=930),
    t(64, 566, 'The recovered depth is relative, not metric', 36, True, color=TEAL, width=1024),
], images=[img('media/moge1/camera-recovery.png', [64, 122, 1024, 179], 'MoGe 1 inference and camera-recovery pipeline from Figure 3', fit='contain')],
notes='This is per-image post-processing after the network prediction, not additional training. Every predicted XYZ point corresponds to a known input pixel. MoGe searches for one focal length and one normalized z-axis shift whose perspective projection sends those points back to their pixels with minimum reprojection error. The paper reports an iterative solver that usually converges within ten iterations and takes about 3 ms. Adding the recovered shift produces a scale-invariant camera-space point map and depth map. Global metric scale is still unknown, so this output is relative rather than metric.',
sources=[('MoGe 1 project overview', M1_PAGE), ('MoGe 1, Figure 3', M1_PAPER)]))

SLIDES.append(slide('moge1-normalized-shift', 'Scale disappears into normalized shift', [
    t(64, 44, 'Scale disappears into normalized shift', 50, True),
], scene={'kind': 'normalized-shift', 'bounds': [64, 124, 1024, 486]},
notes='This diagram explains why MoGe does not need a separate scale variable during inference-time camera recovery. Under the centered-principal-point assumption, a candidate point-map scale s and z translation t_z affect reprojection only through their ratio t_z divided by s. Scale 1 with shift 3, scale 10 with shift 30, and scale 100 with shift 300 therefore produce the same normalized shift and the same pixels. More generally, any scale-and-shift pair is represented by one normalized shift. Searching focal length plus normalized shift covers the complete observable reprojection space; global scale remains unobservable without a metric reference.',
sources=[('MoGe 1, Section 3.1 and Equation 2', M1_PAPER)]))

g1, r1 = card(64, 180, 314, 320, 'Global loss', ['All valid points', 'Shared alignment', 'Learn overall layout'], TEAL)
g2, r2 = card(419, 180, 314, 320, 'Local losses', ['Sample 3D anchors', 'Spheres at 3 scales', 'Separate alignment'], GOLD)
g3, r3 = card(774, 180, 314, 320, 'Auxiliary losses', ['Surface normals', 'Infinity mask', 'Only when labeled'], BLUE)
SLIDES.append(slide('moge1-supervision', 'Local selects points; affine aligns them',
    [t(64, 54, 'Local selects points; affine aligns them', 48, True)] + g1 + g2 + g3 +
    [t(64, 548, 'Local regions come from 3D distance, not segmentation masks', 32, color=MUTED)],
    r1 + r2 + r3,
    notes='“Local” and “affine” describe different choices. Local specifies which points enter a comparison; affine specifies the scale-and-translation alignment applied before that comparison. The global loss uses all valid points with one ROE alignment. For each local loss, MoGe samples anchor points in the ground-truth point cloud, gathers all points inside a 3D sphere around each anchor, independently aligns the predicted and target points in that sphere, then measures their error. It is not based on semantic or instance segmentation. The three sphere scales are one quarter, one sixteenth and one sixty-fourth of the projected image-diagonal scale. Normal and infinity-mask losses are enabled only for label sources that support them.',
    sources=[('MoGe 1, Section 3.2 and supplementary algorithms', M1_PAPER)]))

text = [t(64, 44, 'Different sensors support different losses', 50, True),
        t(64, 128, '9M', 68, True, color=TEAL), t(198, 147, 'frames from 21 public datasets', 36, True, width=700),
        t(64, 250, 'Synthetic', 34, True, color=TEAL), t(329, 250, 'SfM / MVS', 34, True, color=GOLD, width=213),
        t(594, 250, 'LiDAR', 34, True, color=BLUE, width=213), t(859, 250, 'Kinect', 34, True, color=PINK, width=213),
        *lines(64, 318, ['global + 3 local', 'normals + mask'], 30, width=213, leading=43),
        *lines(329, 318, ['global + 2 local', 'validity mask'], 30, width=213, leading=43),
        *lines(594, 318, ['global + local', 'validity mask'], 30, width=213, leading=43),
        *lines(859, 318, ['global geometry', 'validity mask'], 30, width=213, leading=43),
        t(64, 500, 'Batch 256, 250K–500K pixels, aspect ratio 1:2 to 2:1', 34, True),
        t(64, 554, 'Use only the losses each label source can support', 32, color=MUTED)]
SLIDES.append(slide('moge1-training', 'Different sensors support different losses', text,
    [(48, 228, 245, 235, PANEL), (313, 228, 245, 235, PANEL), (578, 228, 245, 235, PANEL), (843, 228, 245, 235, PANEL)],
    notes='MoGe 1 uses about nine million frames from 21 datasets. The supplement assigns dataset types by label source and quality, then enables different loss combinations. The main paper reports ViT and decoder initial learning rates of 5e-6 and 5e-5, decay by 5 every 100K iterations, batch size 256, randomized aspect ratio and image area, color jitter, blur, JPEG degradation and perspective cropping. Dataset weights are balanced by DINOv2 nearest-neighbor retrieval against OpenImages rather than raw frame counts.',
    sources=[('MoGe 1, Section 3.3 and Supplement Table 5', M1_PAPER), ('Released v1 training config', CODE)]))

m1a, m1ra = metric_card(64, 'Local XYZ error ↓', 'DUSt3R  7.97', 'MoGe  5.50')
m1b, m1rb = metric_card(417, 'Depth error ↓', 'Marigold  8.41', 'MoGe  4.72')
m1c, m1rc = metric_card(770, 'Mean FOV error ↓', 'WildCam  7.00°', 'MoGe  2.91°')
SLIDES.append(slide('moge1-results', 'MoGe 1 improves geometry and FOV',
    [t(64, 50, 'MoGe 1 improves geometry and FOV', 52, True)] + m1a + m1b + m1c +
    [t(64, 558, 'Zero-shot averages use task-specific benchmark sets and alignments', 32, color=MUTED)],
    m1ra + m1rb + m1rc,
    notes='These are representative averages from different tables, so do not combine them into one score. Local point-map Rel compares MoGe to the strongest listed baseline in Table 1. At evaluation time, local point regions come from benchmark object masks or Segment Anything, then each region receives its own affine alignment. This differs from the training local loss, whose regions are 3D spheres around sampled anchors. Affine-invariant depth Rel aligns depth with one global scale and shift before comparison. FOV mean error compares with WildCam in Table 3. Lower is better for all three displayed numbers. MoGe 1 remains scale ambiguous by design.',
    sources=[('MoGe 1, Tables 1–3', M1_PAPER)]))

SLIDES.append(slide('moge1-demo', 'Inspect the MoGe 1 reconstruction', [
    t(64, 44, 'Inspect the MoGe 1 reconstruction', 52, True),
    t(64, 520, 'Drag to orbit', 32, True, color=TEAL, width=300),
    t(64, 568, 'No metric scale', 30, color=MUTED, width=300),
], images=[img('media/moge1/office.jpg', [64, 170, 300, 300], 'Office input from the MoGe 1 project demo', fit='cover')],
scene={'bounds': [400, 146, 704, 456], **moge1_cloud, 'initial_yaw': 0, 'initial_pitch': 0},
notes='Interactive offline reproduction using sampled vertices and UV colors from the office mesh hosted by the authors. The source image is shown at left. The browser viewer is ours; the geometry and texture come from the official demo asset. Sampling reduces the mesh to about 17K points for responsive presentation. Do not infer metric measurements from this MoGe 1 output.',
sources=[('MoGe 1 interactive project demo', M1_PAGE)]))

SLIDES.append(slide('moge1-video', 'MoGe 1 registers framewise predictions', [
    t(64, 44, 'MoGe 1 registers framewise predictions', 50, True),
], video={'src': 'media/moge1/teaser.mp4', 'poster': 'media/moge1/teaser.jpg',
          'bounds': [96, 128, 960, 480], 'autoplay': False, 'muted': True},
notes='Official 40.8-second project teaser, bundled locally. The project page explains that video results are produced by predicting point maps independently per frame and registering them with rigid similarity transforms from image matching. This is not a jointly inferred temporally consistent video model. Press Play when useful.',
sources=[('MoGe 1 official project video', M1_PAGE)]))


# MoGe 2
SLIDES.append(section('moge2-section', 'MoGe 2', 'Add metric scale and retain relative geometry', GOLD))

left, lr = card(64, 180, 480, 330, 'Entangled target', ['One branch learns shape', 'and metric scale together', 'Scale errors disturb shape'], RED)
right, rr = card(608, 180, 480, 330, 'Decoupled target', ['Point map keeps invariance', 'CLS token predicts scale', 'Separate losses, shared image'], GOLD)
SLIDES.append(slide('moge2-scale-problem', 'Scale errors can disturb relative shape',
    [t(64, 54, 'Scale errors can disturb relative shape', 54, True)] + left + right +
    [t(64, 558, 'Global scale varies far more across open-domain scenes than local shape', 32, color=MUTED)],
    lr + rr,
    notes='MoGe 2 observes that an entangled metric target produces large gradients when scale estimates are wrong, which can damage relative geometry. The paper instead retains MoGe 1’s affine-invariant geometry branch and predicts one positive global scale separately.',
    sources=[('MoGe 2, Sections 3.1–3.2', M2_PAPER)]))

SLIDES.append(slide('moge2-architecture', 'Predict scale separately to protect shape', [
    t(64, 44, 'Predict scale separately to protect shape', 48, True),
    t(64, 438, 'Affine point map preserves relative geometry', 34, True, color=TEAL),
    t(64, 496, 'CLS scale head restores meters', 34, True, color=GOLD),
    t(64, 554, 'The two outputs combine only at the end', 32, color=MUTED),
], images=[img('media/moge2/architecture.png', [48, 138, 1056, 242], 'MoGe 2 Figure 2 model architecture', fit='contain')],
notes='Official MoGe 2 Figure 2, cropped at high resolution from the bundled paper. Dense ViT tokens feed the convolutional neck and point head, which retain MoGe 1’s affine-invariant shape prediction. The global CLS token feeds a small MLP and exponential output, producing one positive scene-scale scalar. The scale target is the robust alignment scale between the predicted affine point map and ground truth, computed online and detached before the scale loss. Multiplying the two outputs yields the metric point map. The supplement also maps UV positional encodings into a unit circle to preserve aspect ratio and removes decoder normalization layers to reduce latency without destabilizing training.',
sources=[('MoGe 2, Figure 2 and Equation 4', M2_PAPER), ('MoGe 2 supplement, architecture details', M2_PAPER)]))

SLIDES.append(slide('moge2-data-refinement', 'Real labels are large but incomplete', [
    t(64, 44, 'Real labels are large but incomplete', 50, True),
    t(64, 404, '1  Train a sharp synthetic-only teacher', 34, True, color=TEAL),
    t(64, 456, '2  Filter local disagreements after robust alignment', 34, True, color=GOLD),
    t(64, 508, '3  Fill holes with log-depth gradients and real boundaries', 34, True, color=BLUE),
    t(64, 566, 'Real appearance stays; synthetic detail supplies the missing structure', 32, color=MUTED),
], images=[img('media/moge2/data-refinement.png', [96, 122, 960, 258], 'MoGe 2 real-data filtering and completion examples', fit='contain')],
notes='LiDAR labels can be temporally misaligned with RGB at boundaries; SfM/MVS labels can miss reflective surfaces and thin structures. MoGe 2 trains a synthetic-only model G_syn, compares its geometry with real labels after multi-scale local ROE alignment, removes inconsistent pixels, and completes filtered areas with a log-depth Poisson objective. Remaining real depth supplies boundary conditions, while synthetic predictions supply local gradients. The figure is cropped from the official paper; full context is in the bundled PDF.',
sources=[('MoGe 2, Section 3.3 and Figures 4–5', M2_PAPER)]))

text = [t(64, 44, 'Mixed sources need different training', 50, True),
        t(64, 142, '8.9M', 62, True, color=GOLD), t(240, 160, 'frames across 24 datasets', 36, True, width=668),
        t(64, 250, '16', 52, True, color=TEAL), t(152, 266, 'synthetic sets', 34, width=220),
        t(421, 250, '3', 52, True, color=BLUE, width=60), t(509, 266, 'LiDAR sets', 34, width=200),
        t(778, 250, '5', 52, True, color=PINK, width=60), t(866, 266, 'SfM datasets', 34, width=220),
        t(64, 378, '120K steps', 38, True), t(421, 378, '32 × A100', 38, True, width=250), t(778, 378, '120 hours', 38, True, width=260),
        t(64, 470, 'Backbone LR 1e−5', 34, color=MUTED), t(421, 470, 'Heads LR 1e−4', 34, color=MUTED, width=280),
        t(778, 470, 'halve every 25K', 34, color=MUTED, width=300),
        t(64, 552, 'The released config preserves dataset-specific sampling and losses', 32, color=TEAL)]
SLIDES.append(slide('moge2-training', 'Mixed sources need different training', text,
    [(48, 228, 325, 110, PANEL), (405, 228, 325, 110, PANEL), (762, 228, 325, 110, PANEL)],
    notes='Main-paper training details: DINOv2 ViT-L backbone, normalization removed from convolutional heads for latency, 120K iterations, 32 A100 GPUs for 120 hours, initial learning rates 1e-5 for the backbone and 1e-4 for neck/heads, halved every 25K steps. The supplement lists 24 datasets totaling about 8.9M frames and their sampling weights. The released v2 config is an executable reference for dataset labels and loss routing, but local paths remain placeholders.',
    sources=[('MoGe 2, Section 4 implementation details', M2_PAPER), ('MoGe 2 supplement, Tables A.1–A.2', M2_PAPER), ('Released v2 training config', CODE)]))

m2a, m2ra = metric_card(64, 'Metric point Rel ↓', 'UniDepth V2  10.1', 'MoGe 2  8.19', GOLD)
m2b, m2rb = metric_card(417, 'Metric depth Rel ↓', 'UniDepth V2  21.3', 'MoGe 2  15.7', GOLD)
m2c, m2rc = metric_card(770, 'Boundary F1 ↑', 'Depth Pro  14.3', 'MoGe 2  17.9', GOLD, '↑')
SLIDES.append(slide('moge2-results', 'MoGe 2 resolves the geometry trilemma',
    [t(64, 50, 'MoGe 2 resolves the geometry trilemma', 52, True)] + m2a + m2b + m2c +
    [t(64, 558, 'Relative shape remains competitive while scale and detail improve', 32, color=MUTED)],
    m2ra + m2rb + m2rc,
    notes='Representative averages from MoGe 2 Tables 2 and 3. Metric point and depth use seven metric-annotated datasets. Boundary F1 averages iBims-1, HAMMER, Sintel and Spring. The paper’s relative-geometry table shows MoGe 1 remains stronger on some global relative metrics, but MoGe 2 has the best average rank across the full relative suite and improves local point error. Do not compare numbers across metric families directly.',
    sources=[('MoGe 2, Tables 1–3', M2_PAPER)]))

SLIDES.append(slide('moge2-demo', 'MoGe 2 geometry carries meters', [
    t(64, 44, 'MoGe 2 geometry carries meters', 52, True),
    t(64, 520, 'Drag to orbit', 32, True, color=GOLD, width=300),
    t(64, 568, 'Geometry is metric', 30, color=MUTED, width=300),
], images=[img('media/moge2/room.jpg', [64, 170, 300, 300], 'Room input from the MoGe 2 project demo', fit='cover')],
scene={'bounds': [400, 146, 704, 456], **moge2_cloud},
notes='Interactive offline reproduction using sampled vertices and UV colors from the official MoGe 2 room mesh. Unlike MoGe 1, the released MoGe 2 geometry is in metric scale. This viewer supports orbiting but not the project page’s exact point-to-point picking. About 17K points are retained for responsive presentation.',
sources=[('MoGe 2 interactive project demo', M2_PAGE)]))

SLIDES.append(slide('moge2-video', 'MoGe 2 shows scale and detail together', [
    t(64, 44, 'MoGe 2 shows scale and detail together', 50, True),
], video={'src': 'media/moge2/teaser.mp4', 'poster': 'media/moge2/teaser.jpg',
          'bounds': [96, 128, 960, 480], 'autoplay': False, 'muted': False},
notes='Official 82.3-second MoGe 2 project video, bundled locally with its original audio. Press Play when useful. The website and paper compare raw unfiltered point clouds to expose output quality rather than relying on mesh cleanup.',
sources=[('MoGe 2 official project video', M2_PAGE)]))


# MoGe 3
SLIDES.append(section('moge3-section', 'MoGe 3', 'Move refinement from the image plane into 3D', PINK))

left, lr = card(64, 176, 480, 342, '2D neighborhood', ['Adjacent pixels may lie', 'on different surfaces', 'Features bleed at occlusion'], RED)
right, rr = card(608, 176, 480, 342, '3D neighborhood', ['Separate surfaces occupy', 'separate sparse voxels', 'Thin geometry stays distinct'], PINK)
SLIDES.append(slide('moge3-problem', 'Image proximity is not 3D proximity',
    [t(64, 54, 'Image proximity is not 3D proximity', 54, True)] + left + right +
    [t(64, 558, 'More 2D decoder capacity does not fix the inductive bias', 32, color=MUTED)],
    lr + rr,
    notes='MoGe 3 identifies an architectural mismatch: dense point maps are decoded on a 2D image grid, so feature aggregation follows pixel proximity. Around occlusions, adjacent pixels can belong to geometrically distant surfaces. A parameter-matched 2D U-Net fails to reproduce the gains of sparse 3D refinement in the paper’s ablation.',
    sources=[('MoGe 3, Introduction and Section 4.5', M3_PAPER)]))

SLIDES.append(slide('moge3-method', 'MoGe 3 refines the point map in 3D', [
    t(64, 44, 'MoGe 3 refines the point map in 3D', 50, True),
    t(64, 520, 'The sparse 3D refiner updates the same point map K times', 34, True, color=PINK, width=1024),
], images=[img('media/moge3/method.svg', [40, 142, 1072, 284], 'Official MoGe 3 pipeline showing the base model and iterative self-guided sparse 3D refiner', fit='contain')],
notes='Official MoGe 3 method figure from the authors’ project page. The base model uses a ViT encoder and point head to produce an initial point map while retaining 2D image features. The self-guided sparse 3D refiner voxelizes the current point map, combines its sparse 3D structure with the 2D features, and passes them through a sparse 3D U-Net. The refined point map is fed back through the same refiner for K iterations. The paper’s implementation uses three refinement steps during training. Log depth is used for the sparse depth coordinate and residual update, so the correction is multiplicative in ordinary depth.',
sources=[('MoGe 3 official method figure', M3_PAGE), ('MoGe 3, Sections 3.2–3.3', M3_PAPER)]))

SLIDES.append(slide('moge3-iterations', 'Refinement improves quickly then saturates', [
    t(64, 44, 'Refinement improves quickly then saturates', 48, True),
    t(64, 586, 'Most local gains arrive in step 1; the model is trained for 3 steps', 30, color=PINK),
], images=[img('media/moge3/iteration-ablation.png', [64, 126, 1024, 432], 'MoGe 3 Figure 4 refinement iterations and accuracy curves', fit='contain')],
notes='This is the official MoGe 3 Figure 4, not a training-loss curve. It varies SSR iterations at inference for the jointly trained ViT-L model. At K=0, the jointly trained base already exceeds the separate MoGe 2 baseline shown by hexagon markers. Local point accuracy rises from 50.26 at K=0 to 54.43 after one step, 55.88 at the trained K=3 setting, and saturates near 56.07 at K=5. Boundary F1 makes nearly its full gain in the first step. Global affine-invariant point accuracy stays around 92 throughout. The model is trained with K=3 but remains stable through K=7, supporting the paper’s claim that the residual corrections are convergent rather than tied to a fixed horizon. Runtime is 39 ms at K=0 and 121 ms at K=3 on one A100; the paper does not report per-step training loss.',
sources=[('MoGe 3, Figure 4 and Section 4.5', M3_PAPER), ('MoGe 3, Table 2 runtime', M3_PAPER)]))

SLIDES.append(slide('moge3-refinement-demo', 'Watch thin structures emerge', [
    t(64, 44, 'Watch thin structures emerge', 50, True),
], scene={'kind': 'steps', 'bounds': [192, 128, 768, 474], 'frames': moge3_steps},
notes='Interactive slider over six clean offline captures of the authors’ official textured geometry viewer. Step 0 is the unrefined base output; steps 1–5 show repeated SSR updates with the official camera held fixed. Use the fence rails to inspect separation and continuity.',
sources=[('MoGe 3 interactive refinement viewer', M3_PAGE)]))

text = [t(64, 44, 'Protect pretrained geometry during warm-up', 48, True)]
cards = []
for x, title, body, color in [
    (64, 'Warm-up', ['Zero-init residual', 'Detach from base', '5K steps'], TEAL),
    (412, 'Joint training', ['Unfreeze all', 'Three SSR steps', 'Global batch 96'], GOLD),
    (760, 'Data routing', ['Base: real + synth', 'Refiner: synth only', 'Use accurate pixels'], PINK),
]:
    c, r = card(x, 176, 304, 340, title, body, color); text += c; cards += r
text += [t(64, 552, 'Let the new refiner learn corrections before it can disturb the base', 32, color=MUTED)]
SLIDES.append(slide('moge3-training', 'Protect pretrained geometry during warm-up', text, cards,
    notes='MoGe 3 uses AdamW, weight decay 1e-2 and gradient clipping at norm 1. Peak learning rates are 2e-4 for the refiner, 1e-4 for 2D heads and 5e-6 for DINO. The backbone is frozen for 1K steps and warmed through step 2K. The refiner is detached from the backbone for the first 5K steps. Training uses 16 A100 GPUs, global batch 96, BF16 for DINO and FP32 elsewhere. Crucially, the base model learns from the full real + synthetic mixture, while SSR receives gradients only from pixel-accurate synthetic samples.',
    sources=[('MoGe 3, Appendix A.2–A.3', M3_PAPER), ('Released v3 training config', CODE)]))

m3a, m3ra = metric_card(64, 'Local point Rel ↓', 'MoGe 2  3.19', 'MoGe 3-L  2.79', PINK)
m3b, m3rb = metric_card(417, 'Local point δ₀.₀₁ ↑', 'MoGe 2  46.6', 'MoGe 3-L  55.9', PINK, '↑')
m3c, m3rc = metric_card(770, 'Metric depth δ₁ ↑', 'MoGe 2  77.3', 'MoGe 3-L  82.7', PINK, '↑')
SLIDES.append(slide('moge3-results', 'The largest gain is local 3D fidelity',
    [t(64, 50, 'The largest gain is local 3D fidelity', 52, True)] + m3a + m3b + m3c +
    [t(64, 558, 'Three SSR steps raise latency from 39 ms to 121 ms on one A100', 32, color=MUTED)],
    m3ra + m3rb + m3rc,
    notes='Table 1 averages global metrics over nine benchmarks, local metrics over Spring and Synth4K, and boundary F1 over four datasets. Displayed comparisons use the ViT-L MoGe 3 model against MoGe 2. Strict local point inlier accuracy rises from 46.6 to 55.9 while metric depth inlier accuracy rises from 77.3 to 82.7. The ViT-G variant improves most global metrics further. Runtime is reported at 700 squared resolution on an A100: 39 ms for MoGe 2 and 121 ms for MoGe 3 ViT-L with three refinement steps.',
    sources=[('MoGe 3, Tables 1–2', M3_PAPER)]))

SLIDES.append(slide('moge3-video', 'Fine geometry survives a new view', [
    t(64, 44, 'Fine geometry survives a new view', 50, True),
], video={'src': 'media/moge3/teaser.mp4', 'poster': 'media/moge3/teaser.jpg',
          'bounds': [96, 128, 960, 480], 'autoplay': False, 'muted': True},
notes='Official 126.5-second project teaser, bundled locally. It was resized from 1920×1080 to 1280×720 for practical offline presentation; duration and visual sequence are unchanged. Press Play when useful. The video emphasizes fine structures and novel-view geometry.',
sources=[('MoGe 3 official project video', M3_PAGE)]))

SLIDES.append(slide('moge3-limits', 'Fine detail is improved, not solved', [
    t(64, 54, 'Fine detail is improved, not solved', 52, True),
    *lines(88, 198, ['Regression still blurs ambiguous boundary pixels',
                     'Fly-points remain near occlusion edges',
                     'Voxel resolution trades detail for sparse occupancy',
                     'Three refinement steps add 82 ms on A100'], 38, leading=78),
    t(64, 548, 'The paper suggests generative boundary modeling as a next direction', 32, color=PINK),
], notes='Limitations from the paper plus its runtime table. MoGe 3 does not claim perfectly sharp edges. The regression formulation cannot fully resolve boundary ambiguity and may create fly-points. In the ablation, voxel resolution D=200 is the best trade-off; D=400 becomes too sparse and harms local and global metrics. Boundary F1 is not the same as local 3D fidelity.',
sources=[('MoGe 3, Limitations and Section 4.5', M3_PAPER)]))


# Synthesis for our training
text = [t(64, 48, 'The series changes one axis at a time', 52, True)]
rects = []
for x, title, line1, line2, color in [
    (64, 'MoGe 1', 'Representation', 'Invariant loss', TEAL),
    (412, 'MoGe 2', 'Data + objective', 'Scale + cleanup', GOLD),
    (760, 'MoGe 3', 'Architecture', 'Sparse 3D refiner', PINK),
]:
    rects.append((x, 176, 304, 310, PANEL))
    text += [t(x + 26, 204, title, 44, True, color=color, width=252),
             t(x + 26, 286, line1, 32, True, width=252),
             t(x + 26, 350, line2, 32, color=MUTED, width=252)]
text += [t(64, 542, 'Protect what already works while adding one capability', 34, True)]
SLIDES.append(slide('series-synthesis', 'The series changes one axis at a time', text, rects,
notes='Synthesis. MoGe 1 changes the representation and supervision. MoGe 2 preserves that shape pathway while adding a separate scale objective and a data-cleaning pipeline. MoGe 3 preserves the base pathway while adding a staged residual refiner. This incremental pattern gives us a safer template than end-to-end fine-tuning every component at once.',
sources=[('MoGe code and training configs', CODE)]))

text = [t(64, 46, 'Small safeguards keep supervision stable', 50, True)]
rects = []
for x, title, body, color in [
    (64, 'MoGe 1', ['Visual balancing', 'Sensor loss routing', 'Camera crop'], TEAL),
    (412, 'MoGe 2', ['Teacher cleanup', 'Detached scale', 'No decoder norm'], GOLD),
    (760, 'MoGe 3', ['Split data streams', 'Detach base for 5K', 'Step-wise losses'], PINK),
]:
    c, r = card(x, 166, 304, 358, title, body, color)
    text += c
    rects += r
text += [t(64, 560, 'The code treats data geometry as carefully as model geometry', 32, color=MUTED)]
SLIDES.append(slide('implementation-safeguards', 'Small safeguards keep supervision stable', text, rects,
    notes='Details worth borrowing from the papers, supplements and official training code. MoGe 1 estimates dataset sampling weights through DINOv2 nearest-neighbor retrieval against OpenImages rather than sampling in proportion to raw dataset size, and routes different loss terms by sensor label type. Its perspective crop updates intrinsics and camera orientation together. In the released loader, crops that retain too little valid depth are rejected and resampled; dense depth is warped in disparity space to better preserve planes, while sparse labels use mask-aware nearest resizing. MoGe 2 uses a synthetic-only teacher to filter and complete imperfect real geometry, detaches the robustly estimated scale target, maps rectangular UV coordinates into a unit circle to preserve aspect ratio, and removes normalization from convolutional decoder blocks for lower latency. MoGe 3 splits real-plus-synthetic base batches from synthetic-only refinement batches, schedules a fixed refinement quota across gradient accumulation, detaches refiner features from the backbone through step 5000, and uses apply_steps to choose which refinement iterations each loss supervises.',
    sources=[('MoGe training guide and released configs', CODE), ('MoGe 1 supplementary training details', M1_PAPER), ('MoGe 2 supplementary architecture and data refinement', M2_PAPER), ('MoGe 3 appendix and released v3 config', M3_PAPER)]))

left, lr = card(64, 170, 500, 360, 'Carry over directly', [
    'Decouple scale from shape',
    'Route losses by label reliability',
    'Use local boundary checks',
    'Warm up new heads first',
], TEAL)
right, rr = card(588, 170, 500, 360, 'Evaluate separately', [
    'Metric scale error',
    'Relative geometry retention',
    'Local thin-structure fidelity',
    'Coverage and rejection rate',
], GOLD)
SLIDES.append(slide('training-lessons', 'Teach scale without rewriting shape',
    [t(64, 48, 'Teach scale without rewriting shape', 54, True)] + left + right +
    [t(64, 566, 'One scale signal should not destabilize a strong dense predictor', 30, color=MUTED)],
    lr + rr,
    notes='Recommendation for our project. Our accidental-size-probe labels primarily add scene scale. The MoGe 2 pattern says to supervise that capability separately from dense affine geometry, with stop-gradient or a frozen geometry branch initially. Confidence masks and label types should decide which losses a sample receives. Evaluation must show both metric improvement and retention of pretrained relative/local geometry, plus acceptance coverage.',
    sources=[('MoGe 2 decoupled scale design', M2_PAPER), ('MoGe 1 label-quality routing', M1_PAPER)]))

SLIDES.append(slide('progress', 'A staged training plan for our data', [
    t(64, 44, 'A staged training plan for our data', 52, True),
    t(64, 148, '1', 46, True, color=TEAL), t(128, 156, 'Freeze geometry and train scale prediction', 36, True),
    t(64, 244, '2', 46, True, color=GOLD), t(128, 252, 'Weight labels by confidence and evidence agreement', 36, True),
    t(64, 340, '3', 46, True, color=BLUE), t(128, 348, 'Unfreeze only after held-out scale improves', 36, True),
    t(64, 436, '4', 46, True, color=PINK), t(128, 444, 'Tune SSR only with pixel-accurate supervision', 36, True),
    t(64, 552, 'Split by physical scene and compare with the unchanged checkpoint', 32, color=MUTED),
], notes='Concrete proposed experiment order. First test whether agent-derived labels can train only a global scale head while freezing dense geometry. Use label confidence, number of accepted probes, dimensional consistency and cross-frame agreement as weights or routing gates. Unfreeze the encoder and dense heads only if the held-out metric gain is real and relative/local geometry is retained. Do not use noisy metric pseudo-labels to supervise SSR detail; follow MoGe 3 and reserve that refiner for pixel-accurate synthetic or carefully validated dense labels. Splits must prevent frames from the same physical scene crossing train and test.',
sources=[('MoGe 2 scale-head training', M2_PAPER), ('MoGe 3 staged training', M3_PAPER)]))

SLIDES.append(slide('training-experiments', 'Isolate supervision in the first ablations', [
    t(64, 44, 'Isolate supervision in the first ablations', 50, True),
    t(64, 148, 'A', 40, True, color=TEAL), t(126, 153, 'Frozen base + scale head', 36, True),
    t(64, 228, 'B', 40, True, color=GOLD), t(126, 233, 'Joint fine-tune with uniform label weights', 36, True),
    t(64, 308, 'C', 40, True, color=BLUE), t(126, 313, 'Joint fine-tune with confidence routing', 36, True),
    t(64, 388, 'D', 40, True, color=PINK), t(126, 393, 'C + refined dense labels for geometry losses', 36, True),
    t(64, 500, 'Primary test', 32, True, color=MUTED),
    t(280, 500, 'metric depth improves and relative geometry holds', 32, width=808),
    t(64, 560, 'Report accepted-label coverage beside accuracy', 32, color=MUTED),
], notes='Proposed minimal ablation matrix. A tests the MoGe 2 hypothesis directly. B tells us whether naive joint fine-tuning damages geometry. C tests whether uncertainty-aware routing matters. D should only be attempted after we have a principled dense-label refinement method; agent scene-scale labels alone are not dense geometry ground truth. Compare each run with the unchanged pretrained MoGe 3 checkpoint on identical held-out inputs.',
sources=[('MoGe 2 ablations, Table 4', M2_PAPER), ('MoGe 3 ablations, Table 3', M3_PAPER)]))

SLIDES.append(slide('discussion', 'What should we borrow first', [
    t(64, 64, 'What should we borrow first', 58, True),
    t(64, 218, '1  Decoupled scale head', 42, True, color=TEAL),
    t(64, 306, '2  Confidence-aware data routing', 42, True, color=GOLD),
    t(64, 394, '3  Staged unfreezing', 42, True, color=PINK),
    t(64, 530, 'Which experiment gives us the fastest falsifiable answer?', 34, color=MUTED),
], notes='Discussion. The suggested first experiment is a frozen MoGe 3 base with a separately trained scale head using our labels. It is the cheapest test of whether our supervision carries a learnable metric signal and has the lowest risk of erasing relative geometry. Capture the decision and owner in presenter notes.',
sources=[('MoGe series code', CODE)]))


# Lead with outputs and quantitative evidence before explaining each paper's method.
SLIDE_ORDER = [
    'recap', 'series-map',
    'moge1-section', 'moge1-video', 'moge1-results',
    'moge1-invariance-demo', 'moge1-ambiguity', 'moge1-affine-invariant',
    'moge1-representation', 'moge1-normalized-shift', 'moge1-supervision', 'moge1-training',
    'moge2-section', 'moge2-video', 'moge2-results',
    'moge2-scale-problem', 'moge2-architecture', 'moge2-data-refinement', 'moge2-training',
    'moge3-section', 'moge3-refinement-demo', 'moge3-video', 'moge3-results',
    'moge3-problem', 'moge3-method', 'moge3-iterations', 'moge3-training', 'moge3-limits',
    'series-synthesis', 'implementation-safeguards', 'training-lessons',
    'progress', 'training-experiments', 'discussion',
]
_slides_by_id = {item['id']: item for item in SLIDES}
SLIDES = [_slides_by_id[identity] for identity in SLIDE_ORDER]
