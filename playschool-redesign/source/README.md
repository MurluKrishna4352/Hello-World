# Source: how the redesign images and the video were produced

## Virtual staging (`stage/`)
Python 3 with `opencv-python-headless numpy pillow scipy`, plus Node 22 with `three@0.170.0` and `playwright` (run `npm i` in `stage/web`).

```bash
cd stage
python fit.py hall_arch hall_entry arch door ext_wide backroom   # solve the camera per frame -> out/<scene>_cam.json + overlay check
python sc_ext.py door && python sc_ext.py ext_wide              # facade + entrance
python sc_hall.py entry && python sc_hall.py play && python sc_hall.py training && python sc_hall.py arch
python sc_class.py                                              # classroom
# results: stage/final/<scene>_before.jpg / _after.jpg
```
`frames/` holds the key frames from the original walkthrough video (times: facade 0.0 s, door 2.9 s, entry 7.9 s,
hall 12.5 s, arch 14.0 s, back room 18.8 s). To rename the school, edit `SCHOOL` in `stage/sc_ext.py`.

## Video (`video/`)
These scripts run inside a video-editing-system project (HyperFrames):
- `grade.py`: brightens the dark back rooms of the source (smoothed auto-exposure); the original file is not modified.
- `build_edl.py`: scene-based edit (EDL), with real footage segments and inserts for the after-reveals.
- `make_frags.py`: all titles, before/after wipes, 3D-anchored callouts, the floor plan, the outro and the audio cues.
- `music.py`: procedural, license-free music bed.

Then `hf_build.py compile`, followed by `render_final.py final` (render, two-pass loudness master to −14 LUFS, verification).
