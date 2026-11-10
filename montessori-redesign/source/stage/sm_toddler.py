"""Back room -> MONTESSORI TODDLER COMMUNITY (18 months - 3 years). World origin = floor corner; wall A z=0 (x<0), wall B x=0."""
import os

import numpy as np

os.environ.setdefault("STAGE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_m"))
os.makedirs(os.environ["STAGE_OUT"], exist_ok=True)

from art import Svg  # noqa: E402
from art_m import framed_print, oak_floor, wainscot  # noqa: E402
from scenekit import Stage  # noqa: E402

st = Stage("backroom", bright=True, denoise=6)
LH, LD = 2.2, st.dims["LD"]
H, XA, ZB = 3.0, -4.6, 4.2
UP = "#eef1e6"            # pale sage-white
OCC = [[(0, 0), (60, 0), (120, 480), (0, 480)]]
DOORWAY = [[(80, 148), (123, 148), (123, 280), (84, 284)]]


def wall_a():
    L = -XA
    s = Svg(L, LH)
    s.rect(0, 0, L, LH, UP)
    wainscot(s, 0, L, top=0.78)
    return s.render("m_tod_a")


def wall_b():
    s = Svg(ZB, H)
    s.rect(0, 0, ZB, H, UP)
    wainscot(s, 0, ZB, top=0.78)
    for z, v, cap in [(0.55, "leaf", "leaf"), (1.0, "bird", "bird"), (1.45, "tree", "tree")]:
        framed_print(s, z, 0.86, 0.3, 0.38, v, cap)
    return s.render("m_tod_b")


a_png, b_png = wall_a(), wall_b()
fl_png = oak_floor(-XA, ZB + 2, "m_tod_floor")

m_occ = st.mask(include_src=OCC, feather=1.5)
keep = 1 - np.clip(m_occ + st.mask(include_src=DOORWAY, feather=1.5), 0, 1)
m_a = st.mask([[[XA, 0, 0], [0, 0, 0], [0, LH - 0.08, 0], [XA, LH - 0.08, 0]]]) * keep
m_b = st.mask([[[0, 0, 0], [0, 0, ZB], [0, H, ZB], [0, H, 0]]]) * keep
m_loft = st.mask([[[XA, LH - 0.08, LD], [0, LH - 0.08, LD], [0, H, LD], [XA, H, LD]],
                  [[XA, LH - 0.08, 0], [0, LH - 0.08, 0], [0, LH - 0.08, LD], [XA, LH - 0.08, LD]]]) * (1 - m_occ)
m_ceil = st.mask([[[XA, H, 0], [0, H, 0], [0, H, ZB + 2], [XA, H, ZB + 2]]]) * (1 - m_occ)
m_floor = st.mask([[[XA, 0, 0], [0, 0, 0], [0, 0, ZB + 2], [XA, 0, ZB + 2]]]) * (1 - m_occ)

kw = dict(strength=30, iters=4, detail=0.0, clamp=(0.55, 1.4))
m_walls = np.clip(m_a + m_b, 0, 1)
sh_w, _ = st.shading(m_walls, **kw)
sh_w = 0.3 * sh_w + 0.7
st.texture(a_png, [XA, LH, 0], [1, 0, 0], [0, -1, 0], (-XA, LH), mask=m_a, shade=sh_w)
st.texture(b_png, [0, H, 0], [0, 0, 1], [0, -1, 0], (ZB, H), mask=m_b, shade=sh_w)
mc = np.clip(m_ceil + m_loft, 0, 1)
sh_c, _ = st.shading(mc, **kw)
st.paint(mc, "#fbf9f4", 0.2 * sh_c + 0.8)
sh_f, _ = st.shading(m_floor, strength=24, iters=3, detail=0.0, clamp=(0.55, 1.4))
st.texture(fl_png, [XA, 0, 0], [1, 0, 0], [0, 0, 1], (-XA, ZB + 2), mask=m_floor, shade=0.5 * sh_f + 0.5)
m_dw = st.mask(include_src=DOORWAY, feather=1.5) * (1 - m_occ)
st.img = st.img * (1 - m_dw[..., None]) + np.clip(st.img * 1.25, 0, 1) * m_dw[..., None]

room = {"W": -XA, "H": H, "D": ZB + 2, "z0": 0, "x0": XA, "noLeft": True}
light = {"dir": [-0.3, 1.4, 0.9], "sun": 1.25, "hemi": 1.6, "ambient": 0.36, "shadowOpacity": 0.32, "shadowRadius": 9,
         "sky": "#fff7ea", "ground": "#cdb89a"}
objs = [
    {"type": "mirrorBar", "wall": "back", "u": -0.92, "w": 1.05, "h": 0.55},
    {"type": "workrug", "pos": [-0.92, 0, 0.55], "w": 1.3, "d": 0.62, "color": "#e9dcc6", "edge": "#cdb48c"},
    {"type": "mshelf", "wall": "right", "u": 1.3, "preset": "toddler", "w": 1.1, "h": 0.5},
    {"type": "mshelf", "wall": "right", "u": 2.55, "preset": "books", "w": 0.85, "h": 0.55},
    {"type": "weaningTable", "pos": [-1.25, 0, 2.35], "rotY": 90},
    {"type": "cushion", "pos": [-0.45, 0, 2.95], "color": "#d9c7a7", "r": 0.2}, {"type": "cushion", "pos": [-0.35, 0, 3.4], "color": "#b7c4a8", "r": 0.2},
    {"type": "basket", "pos": [-0.25, 0, 1.15], "r": 0.13, "h": 0.12, "fill": "balls"},
    {"type": "plant", "pos": [-0.2, 0, 0.22], "h": 0.75, "pot": "#c8754f", "leaf": "#5c8a4a"},
    {"type": "box", "pos": [XA / 2, LH - 0.08, LD / 2], "size": [-XA, 0.08, LD], "color": "#f4efe6", "radius": 0.01},
    {"type": "panelLight", "pos": [-1.5, H, 1.4], "w": 0.6, "d": 0.6, "ei": 1.2},
    {"type": "rattanPendant", "pos": [-1.25, 2.45, 2.35], "drop": 0.4, "r": 0.2},
]
for i, x in enumerate([-3.1, -2.6, -2.1, -1.6, -1.1, -0.6]):
    objs.append({"type": "basket", "pos": [x, LH, 0.3], "r": 0.17, "h": 0.2})
st.layer3d(objs, room, light, tag="m_tod", occ=m_occ)
st.finish("m_toddler", exposure=1.08, sat=1.0, contrast=1.04, vignette=0.12, warmth=0.015)
print("done toddler")
