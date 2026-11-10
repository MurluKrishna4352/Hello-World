"""MONTESSORI hall: Children's House (3-6), after-hours teacher-training practicum, welcome/transition area, arch."""
import math
import os
import sys

import numpy as np

os.environ.setdefault("STAGE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_m"))
os.makedirs(os.environ["STAGE_OUT"], exist_ok=True)

from art import Svg, rainbow_arc  # noqa: E402
from art_m import (INK, OAK, OAK_D, SAGE, SAGE_D, WARM_WHITE, ellipse_line, framed_print, oak_floor, quote,  # noqa: E402
                   wainscot, world_map)
from scenekit import Stage, arch_poly  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "house"
INPAINT = [[(40, 76), (66, 76), (66, 112), (40, 112)], [(42, 118), (68, 118), (68, 152), (42, 152)], [(48, 203), (82, 203), (82, 238), (48, 238)],
           [(0, 224), (56, 216), (56, 234), (0, 242)], [(22, 326), (42, 326), (42, 348), (22, 348)], [(262, 250), (280, 250), (280, 264), (262, 264)]]
if MODE == "arch":
    st = Stage("arch", inpaint=[[(94, 86), (226, 93), (226, 108), (94, 101)], [(0, 183), (42, 183), (42, 268), (0, 268)],
                                [(246, 79), (360, 81), (360, 97), (246, 95)]])
elif MODE == "entry":
    st = Stage("hall_entry", inpaint=[[(243, 22), (272, 22), (272, 48), (243, 48)]])
else:
    st = Stage("hall_arch", inpaint=INPAINT)
W, H = st.dims["W"], st.dims["H"]
WH, ZMAX, LW = 2.9, 10.0, 9.6
ARCH_C, ARCH_SPRING, ARCH_R = 0.52, 2.09, 0.47
OCC = []
if MODE == "entry":
    OCC = [[(0, 0), (28, 0), (90, 96), (101, 280), (107, 480), (0, 480)], [(297, 0), (360, 0), (360, 335), (302, 335)],
           [(318, 300), (360, 300), (360, 480), (312, 480)]]
ELL = (2.45, 2.55, 0.95, 0.55)   # walking-on-the-line ellipse: centre x, z, semi-axes


# ------------------------------------------------------------------ wall artwork
def back_wall():
    s = Svg(W, WH)
    s.rect(0, 0, W, WH, WARM_WHITE)
    wainscot(s, 0, W)
    rainbow_arc(s, ARCH_C, ARCH_SPRING, ARCH_R + 0.17, 0.05, [OAK_D, OAK, OAK], legs=ARCH_SPRING)
    rainbow_arc(s, ARCH_C, ARCH_SPRING, ARCH_R + 0.19, 0.02, [SAGE], legs=ARCH_SPRING)
    for x, v, cap in [(1.45, "leaf", "leaf"), (2.05, "bird", "bird"), (2.75, "tree", "tree"), (3.4, "sun", "sun")]:
        framed_print(s, x, 1.0, 0.32, 0.4, v, cap)
    quote(s, 2.6, 1.84, "Help me to do it myself.", "Maria Montessori", 0.105)
    return s.render("m_hall_back")


def left_wall():
    L = LW
    s = Svg(L, WH)
    s.rect(0, 0, L, WH, WARM_WHITE)
    wainscot(s, 0, L)
    world_map(s, L - 2.95, 1.08, 1.2, 0.62)
    for z, v in [(4.4, "leaf"), (5.0, "tree")]:
        framed_print(s, L - z, 1.0, 0.32, 0.4, v)
    return s.render("m_hall_left")


def right_wall():
    L = LW
    s = Svg(L, WH)
    s.rect(0, 0, L, WH, WARM_WHITE)
    wainscot(s, 0, L)
    for z, v in [(0.25, "bird"), (2.3, "leaf"), (3.2, "tree")]:
        framed_print(s, z, 1.0, 0.32, 0.4, v)
    return s.render("m_hall_right")


back, leftw, rightw = back_wall(), left_wall(), right_wall()
floor_png = oak_floor(W, ZMAX, "m_oak_floor")
ell_png = ellipse_line(W, 5.0, ELL[0], ELL[1], ELL[2], ELL[3], "m_ellipse")

# ------------------------------------------------------------------ masks + shading
arch_open = arch_poly(ARCH_C, ARCH_SPRING, 0.465, x_l=0.06, x_r=0.975)
m_occ = st.mask(include_src=OCC, feather=1.0) if OCC else 0
m_back = st.mask([[[0, 0, 0], [W, 0, 0], [W, WH, 0], [0, WH, 0]]], exclude=[arch_open]) * (1 - m_occ)
m_left = st.mask([[[0, 0, 0], [0, 0, ZMAX], [0, WH, ZMAX], [0, WH, 0]]]) * (1 - m_occ)
m_right = st.mask([[[W, 0, 0], [W, 0, ZMAX], [W, WH, ZMAX], [W, WH, 0]]]) * (1 - m_occ)
m_walls = np.clip(m_back + m_left + m_right, 0, 1)
ref = st.ref_of(m_walls)
sh_walls, _ = st.shading(m_walls, ref=ref, strength=18, iters=3, detail=0.04)

m_ceil = st.mask([[[0, H, 0], [W, H, 0], [W, H, ZMAX], [0, H, ZMAX]], [[0, WH, 0], [W, WH, 0], [W, H, 0], [0, H, 0]],
                  [[0, WH, 0], [0, WH, ZMAX], [0, H, ZMAX], [0, H, 0]], [[W, WH, 0], [W, WH, ZMAX], [W, H, ZMAX], [W, H, 0]]])
if MODE == "entry":
    m_ceil = st.gate(m_ceil, lmin=0.12) * (1 - st.mask(include_src=OCC, feather=1.0))
else:
    m_ceil = st.gate(m_ceil, lmin=0.42)
sh_ceil, _ = st.shading(m_ceil, strength=22, iters=3, detail=0.0)
st.paint(m_ceil, "#fbf9f4", sh_ceil)

st.texture(back, [0, WH, 0], [1, 0, 0], [0, -1, 0], (W, WH), mask=m_back, shade=sh_walls)
st.texture(leftw, [0, WH, LW], [0, 0, -1], [0, -1, 0], (LW, WH), mask=m_left, shade=sh_walls)
st.texture(rightw, [W, WH, 0], [0, 0, 1], [0, -1, 0], (LW, WH), mask=m_right, shade=sh_walls)

m_floor = st.mask([[[0, 0, 0], [W, 0, 0], [W, 0, ZMAX], [0, 0, ZMAX]]]) * (1 - m_occ)
sh_floor, _ = st.shading(m_floor, strength=14, iters=2, detail=0.12, clamp=(0.45, 1.6))
st.texture(floor_png, [0, 0, 0], [1, 0, 0], [0, 0, 1], (W, ZMAX), mask=m_floor, shade=sh_floor)
st.texture(ell_png, [0, 0, 0], [1, 0, 0], [0, 0, 1], (W, 5.0), mask=m_floor, shade=sh_floor, opacity=0.95)

if MODE in ("arch", "house"):
    m_open = st.mask([arch_open], feather=2.0)
    lift = st.img * 1.5 + 0.03
    st.img = st.img * (1 - m_open[..., None]) + np.clip(lift, 0, 1) * m_open[..., None]

# ------------------------------------------------------------------ 3D: the prepared environment
room = {"W": W, "H": H, "D": ZMAX, "z0": 0}
light = {"dir": [0.35, 1.0, 1.2], "sun": 1.35, "hemi": 1.5, "ambient": 0.32, "shadowOpacity": 0.36, "shadowRadius": 10,
         "sky": "#fff7ea", "ground": "#cdb89a"}


def chair2(x, z, rot, scale=1.0, col=None):
    return {"type": "chair", "pos": [x, 0, z], "rotY": rot, "scale": scale, "color": col or "#d6ae7b", "legs": "#a87a4a"}


house = [
    {"type": "panelLight", "pos": [0.75, H, 0.75], "w": 0.5, "d": 0.5, "ei": 1.0}, {"type": "panelLight", "pos": [0.75, H, 2.3], "w": 0.5, "d": 0.5, "ei": 1.0},
    {"type": "mshelf", "wall": "back", "u": 1.85, "preset": "sensorial"},
    {"type": "mshelf", "wall": "back", "u": 3.2, "preset": "practical"},
    {"type": "mshelf", "wall": "right", "u": 1.15, "preset": "math", "w": 1.0},
    {"type": "mshelf", "wall": "left", "u": 2.3, "preset": "language", "w": 1.3},
    {"type": "mshelf", "wall": "left", "u": 4.05, "preset": "cultural", "w": 1.2},
    {"type": "plant", "pos": [3.9, 0, 0.48], "h": 1.15, "pot": "#c8754f", "leaf": "#5c8a4a"},
    {"type": "rattanPendant", "pos": [1.7, 2.35, 1.8], "drop": 0.5},
    {"type": "rattanPendant", "pos": [2.4, 2.35, 4.4], "drop": 0.5},
    {"type": "bench", "wall": "right", "u": 5.9, "w": 1.0, "d": 0.34, "h": 0.3, "shelf": True, "shoes": True},
    {"type": "hooks", "wall": "right", "u": 5.9, "n": 4, "y": 1.02},
    {"type": "plant", "pos": [3.85, 0, 6.0], "h": 1.25, "pot": "#c8754f", "leaf": "#4f7a3e"},
    {"type": "cushion", "pos": [3.45, 0, 4.6], "color": "#d9c7a7"}, {"type": "cushion", "pos": [3.5, 0, 5.1], "color": "#b7c4a8"},
    {"type": "basket", "pos": [3.8, 0, 4.85], "r": 0.14, "h": 0.16, "fill": "balls"},
]
if MODE == "training":
    objs = [o for o in house if o["type"] not in ("rattanPendant",)]
    objs += [
        {"type": "screen", "wall": "back", "u": 2.55, "v": 1.78, "w": 1.9, "h": 1.05,
         "title": "Montessori Teacher Training", "header": "#6f8160", "lines": ["The prepared environment", "Presenting sensorial materials",
                                                           "Observation & record keeping", "Practical life & grace"]},
        {"type": "projector", "pos": [2.55, H - 0.02, 1.9], "drop": 0.4},
        {"type": "workrug", "pos": [2.4, 0, 1.0], "w": 1.1, "d": 0.7, "with": "beads"},
        {"type": "box", "pos": [2.4, 0, 0.45], "size": [0.36, 0.3, 0.3], "color": "#d6ae7b", "radius": 0.02},
    ]
    cx, cz, R = 2.4, 1.0, 1.05
    for i, a in enumerate([-82, -50, 50, 82, -110]):
        ar = math.radians(a)
        x, z = cx + R * math.sin(ar), cz + R * math.cos(ar)
        rot = math.degrees(math.atan2(cx - x, cz - z))
        objs.append(chair2(x, z, rot, 1.45, ["#c9a26f", "#b98d5c", "#d6ae7b", "#b98d5c", "#c9a26f"][i]))
else:
    objs = house + [
        {"type": "workrug", "pos": [1.85, 0, 1.05], "w": 1.05, "d": 0.65, "with": "tower"},
        {"type": "table", "pos": [3.0, 0, 1.2], "w": 0.66, "d": 0.46, "h": 0.5, "top": "#e3c393", "legs": "#a87a4a"},
        chair2(2.62, 1.2, 90), chair2(3.38, 1.2, -90),
        {"type": "rugBasket", "pos": [3.5, 0, 2.05]},
        {"type": "table", "pos": [2.3, 0, 4.05], "w": 0.66, "d": 0.46, "h": 0.5, "top": "#e3c393", "legs": "#a87a4a"},
        chair2(2.3, 3.7, 0), chair2(2.3, 4.4, 180),
        {"type": "workrug", "pos": [1.75, 0, 5.05], "w": 1.05, "d": 0.65, "with": "rods", "rotY": 8},
    ]
if MODE == "entry":
    objs += [
        {"type": "counter", "pos": [2.42, 0, 6.3], "w": 1.45, "d": 0.55, "mono": True, "text": "Welcome", "textColor": "#5c6b4f",
         "color": "#d6ae7b", "panel": "#f4ecdd", "top": "#e3c393", "stripe": "#a87a4a", "extras": "plant"},
        {"type": "panelLight", "pos": [2.0, H, 6.5], "w": 0.6, "d": 0.6, "ei": 1.0}, {"type": "panelLight", "pos": [2.0, H, 8.2], "w": 0.6, "d": 0.6, "ei": 1.0},
        {"type": "plant", "pos": [3.8, 0, 7.1], "h": 1.2, "pot": "#c8754f", "leaf": "#4f7a3e"},
    ]
st.layer3d(objs, room, light, tag="m_" + MODE, occ=m_occ)
names = {"house": "m_house", "training": "m_training", "entry": "m_entry", "arch": "m_arch"}
st.finish(names[MODE], exposure=(0.97 if MODE == "entry" else 1.1), sat=1.0, contrast=1.03, vignette=0.1, warmth=0.015)
print("done", MODE)
