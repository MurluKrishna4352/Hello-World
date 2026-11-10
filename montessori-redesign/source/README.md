# Source: Montessori redesign

This builds on `../../playschool-redesign/source/` (camera calibration, compositing library, renderer, key frames).
To re-run, copy these files into that `stage/` folder (`web/scene.js` here is the full renderer, including the
Montessori library), then run:

```bash
cd stage
python sm_ext.py door && python sm_ext.py ext_wide
python sm_hall.py entry && python sm_hall.py house && python sm_hall.py training && python sm_hall.py arch
python sm_toddler.py
# results: stage/final_m/m_<scene>_after.jpg
```

Video: `CALM=1 python music.py music_calm.wav 99` makes the gentle music bed, and `make_frags_m.py` writes the
HyperFrames fragments (calm cream/serif theme, before/after wipes, 3D-anchored callouts, Montessori floor plan,
quote outro) into a video-editing-system project that uses the same EDL as the play-school edit.
