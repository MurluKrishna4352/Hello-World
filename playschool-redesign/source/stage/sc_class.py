"""Back room -> CLASSROOM (Nursery / LKG). World origin = floor corner; wall A is z=0 (x<0), wall B is x=0 (z>0)."""
import numpy as np

from art import RAINBOW, Svg, letters, scallop_dado
from scenekit import Stage

st = Stage("backroom", bright=True, denoise=6)
LH, LD = 2.2, st.dims["LD"]
H = 3.0
XA = -4.6        # far end of wall A
ZB = 4.2         # far end of wall B
UP, DADO_C, DADO = "#e6fcf5", "#ffd8a8", 0.9

OCC = [[(0, 0), (60, 0), (120, 480), (0, 480)]]
DOORWAY = [[(80, 148), (123, 148), (123, 280), (84, 284)]]


def wall_a():
    L = -XA
    s = Svg(L, LH)            # u: x from XA (left) to 0 (corner)
    s.rect(0, 0, L, LH, UP)
    scallop_dado(s, 0, L, DADO, DADO_C, r=0.06)
    s.rect(0, 0, L, 0.08, "#ff922b")
    abc = "ABCDE"
    for i, ch in enumerate(abc):
        x = L - 1.78 + i * 0.34
        s.rect(x, 1.84, 0.28, 0.24, RAINBOW[i % 6], f'rx="{0.03 * s.px}"')
        s.text(x + 0.14, 1.89, ch, 0.18, "#ffffff")
    return s.render("class_a")


def wall_b():
    s = Svg(ZB, H)            # u: z from 0 (corner) towards the camera
    s.rect(0, 0, ZB, H, UP)
    scallop_dado(s, 0, ZB, DADO, DADO_C, r=0.06)
    s.rect(0, 0, ZB, 0.08, "#ff922b")
    for i in range(10):
        z = 0.75 + i * 0.32
        s.circle(z, 2.05, 0.12, RAINBOW[i % 6])
        s.text(z, 2.0, str(i + 1), 0.13, "#ffffff")
    s.rect(0.6, 2.04, 3.3, 0.012, "#868e96")
    return s.render("class_b")


a_png, b_png = wall_a(), wall_b()

m_occ = st.mask(include_src=OCC, feather=1.5)
keep = 1 - np.clip(m_occ + st.mask(include_src=DOORWAY, feather=1.5), 0, 1)
m_a = st.mask([[[XA, 0, 0], [0, 0, 0], [0, LH - 0.08, 0], [XA, LH - 0.08, 0]]]) * keep
m_b = st.mask([[[0, 0, 0], [0, 0, ZB], [0, H, ZB], [0, H, 0]]]) * keep
m_loft = st.mask([[[XA, LH - 0.08, LD], [0, LH - 0.08, LD], [0, H, LD], [XA, H, LD]],
                  [[XA, LH - 0.08, 0], [0, LH - 0.08, 0], [0, LH - 0.08, LD], [XA, LH - 0.08, LD]]]) * (1 - m_occ)
m_ceil = st.mask([[[XA, H, 0], [0, H, 0], [0, H, ZB + 2], [XA, H, ZB + 2]]]) * (1 - m_occ)
m_floor = st.mask([[[XA, 0, 0], [0, 0, 0], [0, 0, ZB + 2], [XA, 0, ZB + 2]]]) * (1 - m_occ)

m_walls = np.clip(m_a + m_b, 0, 1)
kw = dict(strength=30, iters=4, detail=0.0, clamp=(0.55, 1.4))
sh_w, ref = st.shading(m_walls, **kw)
sh_w = 0.5 * sh_w + 0.5          # new even LED lighting
st.texture(a_png, [XA, LH, 0], [1, 0, 0], [0, -1, 0], (-XA, LH), mask=m_a, shade=sh_w)
st.texture(b_png, [0, H, 0], [0, 0, 1], [0, -1, 0], (ZB, H), mask=m_b, shade=sh_w)
sh_c, _ = st.shading(np.clip(m_ceil + m_loft, 0, 1), **kw)
st.paint(np.clip(m_ceil + m_loft, 0, 1), "#fbfaf7", 0.2 * sh_c + 0.8)
sh_f, _ = st.shading(m_floor, strength=24, iters=3, detail=0.0, clamp=(0.55, 1.4))
st.paint(m_floor, "#dcc39c", 0.5 * sh_f + 0.5)
# doorway beyond: slightly brighter, cooler
m_dw = st.mask(include_src=DOORWAY, feather=1.5) * (1 - m_occ)
st.img = st.img * (1 - m_dw[..., None]) + np.clip(st.img * 1.25, 0, 1) * m_dw[..., None]

room = {"W": -XA, "H": H, "D": ZB + 2, "z0": 0, "x0": XA, "noLeft": True}
light = {"dir": [-0.3, 1.4, 0.9], "sun": 1.3, "hemi": 1.6, "ambient": 0.35, "shadowOpacity": 0.33, "shadowRadius": 9}
objs = [
    {"type": "board", "kind": "whiteboard", "wall": "back", "u": -0.98, "v": 1.3, "w": 1.45, "h": 0.8, "tray": True,
     "text": "A  B  C", "text2": "1 + 2 = 3"},
    {"type": "board", "kind": "art", "wall": "right", "u": 1.25, "v": 1.42, "w": 1.25, "h": 0.8, "frame": 0.04,
     "frameColor": "#ff922b", "frameMetal": 0, "title": "OUR ART", "seed": 21},
    {"type": "rug", "pos": [-1.75, 0, 1.25], "w": 2.1, "d": 1.3, "style": "alphabet"},
    {"type": "table", "pos": [-1.1, 0, 2.55], "w": 1.1, "d": 0.6, "h": 0.5, "top": "#ffffff", "legs": "#4dabf7", "edge": "#4dabf7"},
    {"type": "chair", "pos": [-1.4, 0, 2.05], "rotY": 0, "color": "#ff6b6b"},
    {"type": "chair", "pos": [-0.8, 0, 2.05], "rotY": 0, "color": "#ffd43b"},
    {"type": "chair", "pos": [-1.4, 0, 3.05], "rotY": 180, "color": "#69db7c"},
    {"type": "chair", "pos": [-0.8, 0, 3.05], "rotY": 180, "color": "#9775fa"},
    {"type": "cubeShelf", "wall": "right", "u": 2.75, "cols": 3, "rows": 2, "fill": "mixed", "seed": 11},
    {"type": "box", "pos": [XA / 2, LH - 0.08, LD / 2], "size": [-XA, 0.08, LD], "color": "#f8f9fa", "radius": 0.01},
    {"type": "toyBoxes", "pos": [-2.2, LH, 0.3], "n": 5, "w": 0.36, "h": 0.24, "d": 0.36, "colors": ["#a5d8ff", "#ffd8a8", "#b2f2bb", "#ffc9c9", "#d0bfff", "#ffec99", "#99e9f2", "#fcc2d7"]},
    {"type": "panelLight", "pos": [-1.5, H, 1.5], "w": 0.6, "d": 0.6, "ei": 1.4},
    {"type": "plant", "pos": [-0.25, 0, 0.3], "h": 0.75},
]
st.layer3d(objs, room, light, tag="class", occ=m_occ)
st.finish("classroom", exposure=1.08, sat=1.05, contrast=1.04, vignette=0.12)
print("done classroom")
