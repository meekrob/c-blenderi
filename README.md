# c-blenderi: create 3d models and animation from data

Steps:

1. Parse data files with lineage, physical coordinates and expression data provided.
2. Map coordinates into a synthetic space to be used as a Python extension to Blender
3. Use Blender template objects (metaballs as nuclei) to move and simulate divisions.
4. Render Animation on HPC

Note: this project is quite dated now, although the data may still be available at the [Waterston Lab Lineaging Project](https://waterston.gs.washington.edu/). The main obsolescence is Blender, which underwent a major version change in the middle of me working on this.

This screenshot may be from a lost video:

<img alt="Screenshot mid-video" src="/media/mid-video-screenshot.png" width=512 height=390>

But this video is live on youtube:

<img alt="Screenshot demo" src="/screenshots/youtube_metaballs_50pc_10s.gif" width=328 height=195>

The animation is based on data from the [Waterston Lab Lineaging Project](https://waterston.gs.washington.edu/), a system that traced the development of *C. elegans* embryos which carry reporter strains for various transcription factors, using imaging to resolve lineages.


