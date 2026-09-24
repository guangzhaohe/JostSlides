# MoGe source record

Retrieved September 24, 2026. All materials are bundled so the deck can be presented without a network connection.

## Title artwork

- `media/moge-title-hero.png` is original artwork generated with OpenAI's built-in image generation tool for this presentation. The prompt requested three abstract forms built from point clouds, sparse voxels and depth layers, with true-black negative space for the title. It contains no source-paper figure content

## MoGe 1

- Paper and appended supplement: [arXiv 2410.19115](https://arxiv.org/abs/2410.19115), stored as `moge1.pdf`
- Project page and official teaser: [MoGe](https://wangrc.site/MoGePage/)
- Code and released training configuration: [microsoft/MoGe](https://github.com/microsoft/MoGe)
- `media/moge1/overview.png` is the official project overview
- `media/moge1/focal-distance-ambiguity.png` and `camera-recovery.png` are clean crops of Figures 4 and 3 from the bundled paper. The figure content was not redrawn
- `moge1-normalized-shift` is an original interactive explanation built into the local presenter, based on the normalized z-shift derivation in Section 3.1 and Equation 2 of the paper
- `media/moge1/office.jpg` and `evidence/moge1-office-cloud.json` derive from the official office gallery input and GLB mesh. The mesh was sampled with `scripts/import_glb_cloud.py`; texture colors and source OpenGL coordinates were retained. The canvas projection maps the GLB’s positive-Y-up convention to upward screen motion
- `media/moge1/teaser.mp4` is the official project teaser. `teaser.jpg` is a locally extracted poster frame

## MoGe 2

- Paper: [NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/336572db3e99930814d6b328d4220cb6-Abstract-Conference.html), stored as `moge2.pdf`
- Official supplementary PDF from the NeurIPS proceedings, stored as `moge2-supplement.pdf`
- Project page and official teaser: [MoGe-2](https://wangrc.site/MoGe2Page/)
- Code and released training configuration: [microsoft/MoGe](https://github.com/microsoft/MoGe)
- `media/moge2/architecture.png` is a high-resolution crop of Figure 2. `data-refinement.png` is a high-resolution crop of Figure 4 from the bundled paper. No figure content was redrawn
- `media/moge2/room.jpg` and `evidence/moge2-room-cloud.json` derive from the official room gallery input and GLB mesh. The same local sampler was used
- `media/moge2/teaser.mp4` is the official project video with original audio. `teaser.jpg` is a locally extracted poster frame

## MoGe 3

- Paper and appendix: [arXiv 2607.17967](https://arxiv.org/abs/2607.17967), stored as `moge3.pdf`
- Project page, interactive refinement stages and official teaser: [MoGe-3](https://qft-333.github.io/moge3page/)
- Code and released training configuration: [microsoft/MoGe](https://github.com/microsoft/MoGe)
- `media/moge3/method.svg`, `refiner.svg` and `refinement.svg` are official project diagrams
- `media/moge3/iteration-ablation.png` is a high-resolution crop of Figure 4 from the bundled paper, showing inference accuracy across refinement iterations
- `normal-step0.png` through `normal-step5.png` are clean captures of the official textured refinement viewer at steps 0–5 with the official camera held fixed. The filenames are retained to preserve deck references
- `media/moge3/teaser.mp4` is the complete official teaser resized from 1920 × 1080 to 1280 × 720 with H.264 CRF 23. `teaser.jpg` is a locally extracted poster frame

Numbers shown on slides are transcribed from the cited paper tables. Speaker notes state when displayed values come from different datasets, alignments or metric families.
