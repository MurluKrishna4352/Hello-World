"""MONTESSORI exterior: front door close-up and full facade (world origin = bottom-left of the door, facade plane z=0)."""
import os
import sys

import numpy as np

os.environ.setdefault("STAGE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_m"))
os.makedirs(os.environ["STAGE_OUT"], exist_ok=True)

from art import Svg  # noqa: E402
from art_m import INK, OAK_D, SAGE, SAGE_D, green_wall, leaf_logo, wood_slats  # noqa: E402
from scenekit import Stage  # noqa: E402

SCHOOL = "Little Sprouts"
WHICH = sys.argv[1] if len(sys.argv) > 1 else "door"
FX0, FX1, FH = -0.65, 2.95, 2.05
WALL, PLINTH = "#f1ebdf", "#8c8379"


def facade_art():
    s = Svg(FX1 - FX0, FH)
    L = lambda x: x - FX0  # noqa: E731
    s.rect(0, 0, FX1 - FX0, FH, WALL)
    wood_slats(s, L(-0.33), L(0.0), 0.32, FH)           # oak slat cladding either side of the door
    wood_slats(s, L(1.0), L(1.33), 0.32, FH)
    wood_slats(s, L(-0.33), L(1.33), 1.93, FH)
    green_wall(s, L(-0.6), L(-0.38), 0.5, 1.85)         # narrow vertical garden on the left wall
    s.rect(0, 0, FX1 - FX0, 0.32, PLINTH)                # stone-grey plinth
    s.rect(0, 0.32, FX1 - FX0, 0.02, "#d8cfc2")
    # timings board in an oak frame, under the window
    bx0, bx1, by0, by1 = L(1.45), L(2.86), 0.4, 0.8
    s.rect(bx0 - 0.025, by0 - 0.025, bx1 - bx0 + 0.05, by1 - by0 + 0.05, OAK_D, f'rx="{0.01 * s.px}"')
    s.rect(bx0, by0, bx1 - bx0, by1 - by0, "#fbf7ef")
    s.text((bx0 + bx1) / 2, 0.69, "Admissions open", 0.068, SAGE_D, weight=600, family="Lora")
    s.text((bx0 + bx1) / 2, 0.575, "Toddlers 1.5–3 · Children's House 3–6", 0.047, INK, weight=500)
    s.text((bx0 + bx1) / 2, 0.47, "Teacher training · evenings &amp; weekends", 0.047, INK, weight=500)
    return s.render("m_facade")


def sign_art():
    s = Svg(3.22, 0.6)
    s.rect(0, 0, 3.22, 0.6, "#f6f0e4")
    leaf_logo(s, 0.33, 0.3, 1.2)
    s.text(1.72, 0.27, f"{SCHOOL} Montessori", 0.172, "#4a4540", weight=600, family="Lora")
    s.text(1.72, 0.09, "CHILDREN'S HOUSE  ·  TEACHER TRAINING CENTRE", 0.058, SAGE_D, weight=500)
    return s.render("m_sign")


def banner_art(kind):
    if kind == 1:
        s = Svg(2.2, 0.42)
        s.rect(0, 0, 2.2, 0.42, "#f6f0e4")
        s.rect(0, 0, 0.06, 0.42, SAGE)
        s.text(1.13, 0.22, "Montessori Children's House", 0.11, "#4a4540", weight=600, family="Lora")
        s.text(1.13, 0.08, "TODDLERS &amp; AGES 3–6  ·  CLASSROOMS ON THIS FLOOR", 0.05, SAGE_D, weight=500)
    else:
        s = Svg(2.0, 0.42)
        s.rect(0, 0, 2.0, 0.42, SAGE_D)
        s.text(1.0, 0.22, "Montessori Teacher Training", 0.105, "#ffffff", weight=600, family="Lora")
        s.text(1.0, 0.08, "DIPLOMA COURSES  ·  WORKSHOPS  ·  OBSERVATION", 0.05, "#f1ead9", weight=500)
    return s.render(f"m_banner{kind}")


facade, sign = facade_art(), sign_art()
b1, b2 = banner_art(1), banner_art(2)

st = Stage(WHICH)
d = st.dims
dh, wx, wb = d["dh"], d["wx"], d["wb"]
door = [[0.0, 0, 0], [1.0, 0, 0], [1.0, dh, 0], [0.0, dh, 0]]
window = [[wx - 0.03, wb - 0.04, 0], [3.2, wb - 0.04, 0], [3.2, dh + 0.06, 0], [wx - 0.03, dh + 0.06, 0]]
if WHICH == "door":
    m_wall = st.mask([[[FX0, 0, 0], [FX1, 0, 0], [FX1, FH, 0], [FX0, FH, 0]]], exclude=[door, window],
                     exclude_src=[[(0, 0), (76, 0), (76, 345), (0, 345)]])
    soffit_src = [[(76, 52), (360, 50), (360, 96), (76, 96)]]
else:
    m_wall = st.mask([[[FX0 + 0.08, 0, 0], [2.82, 0, 0], [2.82, FH + 0.15, 0], [FX0 + 0.08, FH + 0.15, 0]]], exclude=[door, window])
    soffit_src = [[(96, 244), (330, 246), (330, 258), (96, 256)]]

sh_wall, _ = st.shading(st.gate(m_wall, lmin=0.1), strength=10, iters=1, detail=0.3, clamp=(0.45, 1.45))
st.texture(facade, [FX0, FH, 0], [1, 0, 0], [0, -1, 0], (FX1 - FX0, FH), mask=m_wall, shade=sh_wall)
m_sof = st.mask(include_src=soffit_src)
yy = np.linspace(0.8, 0.95, m_sof.shape[0])[:, None] * np.ones((1, m_sof.shape[1]))
st.paint(m_sof, "#f4efe6", yy.astype(np.float32))
m_door = st.mask([door], feather=0.8)
sh_door, _ = st.shading(m_door, strength=6, iters=1, detail=0.6, gamma=0.85, clamp=(0.22, 2.0))
st.paint(m_door, "#7f9270", sh_door)                     # sage-green door, grille kept

if WHICH == "ext_wide":
    st.quad_texture(b1, [(118, 195), (252, 196), (252, 220), (118, 219)])
    st.quad_texture(b2, [(140, 115), (230, 115), (230, 134), (140, 134)])

room = {"W": 3.8, "H": 2.6, "D": 3.0, "z0": 0, "x0": -0.7, "noLeft": True, "noRight": True}
light = {"dir": [0.9, 1.1, 0.9], "sun": 2.1, "hemi": 1.3, "ambient": 0.3, "shadowOpacity": 0.42, "shadowRadius": 5, "sky": "#eaf4ff"}
objs = [
    {"type": "signBox", "wall": "back", "u": 1.06, "v": 2.33, "w": 3.22, "h": 0.6, "t": 0.07, "src": "/art/m_sign.png",
     "edge": "#a87a4a", "glow": 0.18},
    {"type": "planter", "pos": [-0.43, 0, 0.3], "w": 0.34, "h": 0.55, "d": 0.34, "color": "#b9704d", "seed": 4, "natural": True, "tall": 0.55},
    {"type": "planter", "pos": [1.3, 0, 0.28], "w": 0.34, "h": 0.55, "d": 0.34, "color": "#b9704d", "seed": 9, "natural": True, "tall": 0.55},
    {"type": "rug", "pos": [0.5, 0, 0.32], "w": 0.95, "d": 0.5, "style": "plain", "color": "#cdb48c", "border": "#a88a5c"},
    {"type": "bench", "pos": [2.15, 0, 0.3], "w": 1.05, "d": 0.36, "h": 0.44},
]
if WHICH == "ext_wide":
    for x, y, w in [(-0.6, 3.26, 0.45), (2.12, 3.26, 0.45), (-0.2, 4.7, 0.36), (1.72, 4.71, 0.36)]:
        objs.append({"type": "planter", "pos": [x, y, 0.95], "w": w, "h": 0.14, "d": 0.18, "color": "#a87a4a", "seed": int(x * 10) + 20, "natural": True, "trail": True})
st.layer3d(objs, room, light, tag="m_ext")
st.finish("m_" + WHICH, exposure=1.04, sat=1.0, contrast=1.02, vignette=0.08, warmth=0.01)
print("done", WHICH)
