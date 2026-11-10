"""Hall (looking towards the arch): PLAY AREA, and the same room in TEACHER TRAINING mode."""
import sys

import numpy as np

from art import (RAINBOW, SOFT_RAINBOW, Svg, bird, butterfly, cloud, flower, footprint, hill, letters, rainbow_arc,
                 scallop_dado, sun, train, tree)
from scenekit import Stage, arch_poly

MODE = sys.argv[1] if len(sys.argv) > 1 else "play"
INPAINT = [[(40,76),(66,76),(66,112),(40,112)], [(42,118),(68,118),(68,152),(42,152)], [(48,203),(82,203),(82,238),(48,238)],
           [(0,224),(56,216),(56,234),(0,242)], [(22,326),(42,326),(42,348),(22,348)], [(262,250),(280,250),(280,264),(262,264)]]
ART = "play" if MODE in ("play", "entry", "arch") else MODE
if MODE == "arch":
    st = Stage("arch", inpaint=[[(94, 86), (226, 93), (226, 108), (94, 101)], [(0, 183), (42, 183), (42, 268), (0, 268)],
                                [(246, 79), (360, 81), (360, 97), (246, 95)]])
elif MODE == "entry":
    st = Stage("hall_entry", inpaint=[[(243, 22), (272, 22), (272, 48), (243, 48)]])
else:
    st = Stage("hall_arch", inpaint=INPAINT)
ZMAX, LW = 10.0, 9.6
OCC = []          # foreground occluders (source px) that must never be repainted
FAN = []
if MODE == "entry":
    OCC = [[(0, 0), (28, 0), (90, 96), (101, 280), (107, 480), (0, 480)],
           [(297, 0), (360, 0), (360, 335), (302, 335)],
           [(318, 300), (360, 300), (360, 480), (312, 480)]]
    FAN = [[(188, 138), (248, 138), (248, 172), (188, 172)]]
W, H = st.dims["W"], st.dims["H"]
WH = 2.9          # painted wall height (cornice above stays white)
DADO = 1.0
UPPER = "#fff6e6"
LOWER = "#a5d8ff"
ARCH_C, ARCH_SPRING, ARCH_R = 0.52, 2.09, 0.47

# ------------------------------------------------------------------ wall artwork
def back_wall(mode):
    s = Svg(W, WH)
    s.rect(0, 0, W, WH, UPPER)
    scallop_dado(s, 0, W, DADO, LOWER)
    s.rect(0, 0, W, 0.09, "#4dabf7")                      # skirting
    # rainbow trim around the arch
    rainbow_arc(s, ARCH_C, ARCH_SPRING, ARCH_R + 0.3, 0.05, RAINBOW, legs=ARCH_SPRING)
    if mode == "play":
        rainbow_arc(s, 2.75, 1.05, 1.15, 0.075, SOFT_RAINBOW)
        hill(s, 1.25, 3.0, DADO + 0.02, 1.55, "#8ce99a")
        hill(s, 2.3, 4.04, DADO + 0.02, 1.62, "#69db7c")
        tree(s, 1.45, 1.2, 0.5)
        tree(s, 3.95, 1.25, 0.45, "#37b24d")
        sun(s, 3.62, 2.3, 0.17)
        cloud(s, 1.65, 2.32, 0.8)
        cloud(s, 2.85, 2.45, 0.65)
        for bx, by in [(2.2, 2.2), (2.35, 2.28), (3.1, 2.1)]:
            bird(s, bx, by, 1.0)
        for fx, col in [(1.35, "#f783ac"), (1.6, "#ffa94d"), (2.0, "#9775fa"), (3.9, "#ff6b6b")]:
            flower(s, fx, 0.6, 0.045, col)
        butterfly(s, 2.45, 0.75, 1.2)
        letters(s, 2.75, 1.66, "PLAY  LEARN  GROW", 0.11, ["#e03131", "#f08c00", "#1971c2", "#2f9e44", "#9c36b5"], gap=0.0)
    else:
        sun(s, 3.75, 2.45, 0.11, face=False)
        cloud(s, 1.45, 2.5, 0.5)
    return s.render(f"hall_back_{mode}")


def left_wall():
    L = LW
    s = Svg(L, WH)          # x=0 at the front (z=L), x=L at the back corner (z=0)
    s.rect(0, 0, L, WH, UPPER)
    scallop_dado(s, 0, L, DADO, LOWER)
    s.rect(0, 0, L, 0.09, "#4dabf7")
    train(s, L - 2.55, 1.3, list("ABCD"), h=0.26)
    for i, (bx, col) in enumerate([(L - 2.4, "#ff8787"), (L - 1.95, "#ffd43b"), (L - 1.5, "#74c0fc"), (L - 1.05, "#8ce99a"), (L - 0.6, "#b197fc")]):
        s.add(f'<line x1="{s.X(bx):.1f}" y1="{s.Y(1.95):.1f}" x2="{s.X(bx + 0.05):.1f}" y2="{s.Y(2.25):.1f}" stroke="#868e96" stroke-width="3"/>')
        s.add(f'<ellipse cx="{s.X(bx + 0.05):.1f}" cy="{s.Y(2.38):.1f}" rx="{0.11 * s.px:.1f}" ry="{0.14 * s.px:.1f}" fill="{col}"/>')
        s.text(bx + 0.05, 2.33, str(i + 1), 0.13, "#ffffff")
    for fx in np.arange(0.5, L, 0.55):
        flower(s, fx, 0.55, 0.04, RAINBOW[int(fx * 3) % 6])
    return s.render("hall_left")


def right_wall():
    L = LW
    s = Svg(L, WH)          # x=0 at back corner (z=0) towards the front
    s.rect(0, 0, L, WH, UPPER)
    scallop_dado(s, 0, L, DADO, LOWER)
    s.rect(0, 0, L, 0.09, "#4dabf7")
    tree(s, 0.75, DADO, 1.3, "#40c057")
    for bx, by in [(0.35, 2.3), (1.3, 2.1)]:
        bird(s, bx, by, 1.2)
    cloud(s, 1.6, 2.45, 0.55)
    return s.render("hall_right")


def floor_mats():
    x0, x1, z1 = 1.12, W, 5.4
    s = Svg(x1 - x0, z1)
    s.add(f'<rect x="0" y="0" width="{(x1 - x0) * s.px}" height="{z1 * s.px}" fill="#ffffff"/>')
    cols = ["#a5d8ff", "#b2f2bb", "#ffec99", "#ffc9c9", "#d0bfff", "#99e9f2"]
    t = 0.6
    nx, nz = int(np.ceil((x1 - x0) / t)), int(np.ceil(z1 / t))
    for i in range(nx):
        for j in range(nz):
            c = cols[(i * 2 + j * 3) % len(cols)]
            X, Z = i * t * s.px, j * t * s.px
            tp = t * s.px
            # tile body with jigsaw teeth
            d = f"M{X},{Z} "
            teeth = 4
            for k in range(teeth):
                a = X + tp * k / teeth
                b = X + tp * (k + 0.5) / teeth
                cc = X + tp * (k + 1) / teeth
                d += f"L{a},{Z} L{b},{Z + (8 if k % 2 else -8)} L{cc},{Z} "
            d += f"L{X + tp},{Z + tp} L{X},{Z + tp} Z"
            s.add(f'<path d="{d}" fill="{c}" stroke="#ffffff" stroke-width="3"/>')
            s.add(f'<rect x="{X + 3}" y="{Z + 3}" width="{tp - 6}" height="{tp - 6}" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="4"/>')
    # border strip along the walkway edge
    s.add(f'<rect x="0" y="0" width="{0.06 * s.px}" height="{z1 * s.px}" fill="#4dabf7"/>')
    return s.render("hall_mats")


def footprints():
    s = Svg(1.2, 9.0)        # floor texture: x 0..1.2, rows = z 0..4.0 (top row = back wall)
    for i, z in enumerate(np.arange(0.55, 8.9, 0.36)):
        col = RAINBOW[i % 6]
        x = 0.5 + (0.09 if i % 2 else -0.09)
        # texture y axis runs with z here, Svg.Y flips so pass (h - z)
        footprint(s, x, 9.0 - z, 0.12, col, rot=180, mirror=bool(i % 2))
    return s.render("hall_steps")


back = back_wall(ART)
leftw = left_wall()
rightw = right_wall()
mats = floor_mats()
steps = footprints()

# ------------------------------------------------------------------ masks + shading
arch_open = arch_poly(ARCH_C, ARCH_SPRING, 0.465, x_l=0.06, x_r=0.975)
m_back = st.mask([[[0, 0, 0], [W, 0, 0], [W, WH, 0], [0, WH, 0]]], exclude=[arch_open])
m_left = st.mask([[[0, 0, 0], [0, 0, ZMAX], [0, WH, ZMAX], [0, WH, 0]]])
m_right = st.mask([[[W, 0, 0], [W, 0, ZMAX], [W, WH, ZMAX], [W, WH, 0]]])
m_occ = st.mask(include_src=OCC, feather=1.0) if OCC else 0
m_back, m_left, m_right = [m * (1 - m_occ) for m in (m_back, m_left, m_right)]
m_walls = np.clip(m_back + m_left + m_right, 0, 1)
ref = st.ref_of(m_walls)
kw = dict(strength=18, iters=3, detail=0.05)
sh_walls, _ = st.shading(m_walls, ref=ref, **kw)

# ceiling + cornice band (exclude the dark fan)
m_ceil = st.mask([[[0, H, 0], [W, H, 0], [W, H, ZMAX], [0, H, ZMAX]],
                  [[0, WH, 0], [W, WH, 0], [W, H, 0], [0, H, 0]],
                  [[0, WH, 0], [0, WH, ZMAX], [0, H, ZMAX], [0, H, 0]],
                  [[W, WH, 0], [W, WH, ZMAX], [W, H, ZMAX], [W, H, 0]]])
if MODE == "entry":
    fanbox = st.mask(include_src=FAN, feather=1.0)
    m_ceil = st.gate(m_ceil, lmin=0.12) * (1 - st.mask(include_src=OCC, feather=1.0))
else:
    m_ceil = st.gate(m_ceil, lmin=0.42)
sh_ceil, _ = st.shading(m_ceil, strength=22, iters=3, detail=0.0)
st.paint(m_ceil, "#fbfaf6", sh_ceil)

st.texture(back, [0, WH, 0], [1, 0, 0], [0, -1, 0], (W, WH), mask=m_back, shade=sh_walls)
st.texture(leftw, [0, WH, LW], [0, 0, -1], [0, -1, 0], (LW, WH), mask=m_left, shade=sh_walls)
st.texture(rightw, [W, WH, 0], [0, 0, 1], [0, -1, 0], (LW, WH), mask=m_right, shade=sh_walls)

# floor
m_floor = st.mask([[[0, 0, 0], [W, 0, 0], [W, 0, ZMAX], [0, 0, ZMAX]]]) * (1 - m_occ)
sh_floor, _ = st.shading(m_floor, strength=16, iters=2, detail=0.15)
m_walk = st.mask([[[0, 0, 0], [1.12, 0, 0], [1.12, 0, 5.4], [W, 0, 5.4], [W, 0, ZMAX], [0, 0, ZMAX]]])
m_walk = m_walk * (1 - m_occ)
sh_walk, _ = st.shading(m_walk, strength=12, iters=2, detail=0.35)
st.paint(m_walk, "#e6d3b3", sh_walk)
if MODE in ("play", "entry", "arch"):
    st.texture(mats, [1.12, 0, 0], [1, 0, 0], [0, 0, 1], (W - 1.12, 5.4), mask=m_floor, shade=sh_floor)
    st.texture(steps, [0.0, 0, 0], [1, 0, 0], [0, 0, 1], (1.2, 9.0), mask=m_floor, shade=sh_floor)
else:
    st.texture(mats, [1.12, 0, 0], [1, 0, 0], [0, 0, 1], (W - 1.12, 5.4), mask=m_floor, shade=sh_floor)

if MODE in ("arch", "play"):
    m_open = st.mask([arch_open], feather=2.0)
    lift = st.img * 1.55 + 0.03
    st.img = st.img * (1 - m_open[..., None]) + np.clip(lift, 0, 1) * m_open[..., None]

# ------------------------------------------------------------------ 3D furniture
room = {"W": W, "H": H, "D": ZMAX, "z0": 0}
light = {"dir": [0.35, 1.0, 1.2], "sun": 1.5, "hemi": 1.45, "ambient": 0.3, "shadowOpacity": 0.38, "shadowRadius": 10}
common = [
    {"type": "panelLight", "pos": [0.75, H, 0.75], "w": 0.5, "d": 0.5}, {"type": "panelLight", "pos": [0.75, H, 2.3], "w": 0.5, "d": 0.5},
]
if MODE in ("play", "entry", "arch"):
    objs = common + [
        {"type": "ballPit", "pos": [3.3, 0, 0.78], "r": 0.62, "color": "#f783ac", "seed": 7},
        {"type": "slide", "pos": [1.72, 0, 0.62], "rotY": 90, "side": "#4dabf7", "chute": "#ffd43b", "step": "#ff6b6b"},
        {"type": "softBlocks", "pos": [2.55, 0, 2.45], "rotY": -20, "scale": 0.8},
        {"type": "cubeShelf", "wall": "left", "u": 2.4, "cols": 4, "rows": 2, "fill": "bins", "topToys": True, "seed": 3},
        {"type": "beanbag", "pos": [1.75, 0, 1.75], "color": "#ffa94d", "r": 0.3},
        {"type": "bunting", "from": [0.02, 2.62, 0.7], "to": [W - 0.02, 2.62, 0.9], "sag": 0.3, "n": 15},
        {"type": "bunting", "from": [0.02, 2.55, 2.4], "to": [W - 0.02, 2.55, 2.6], "sag": 0.3, "n": 15, "colors": ["#4dabf7", "#ffd43b", "#ff6b6b", "#69db7c"]},
        {"type": "cloudLamp", "pos": [1.9, 2.2, 1.2], "drop": 0.5, "s": 0.8},
        {"type": "plant", "pos": [3.85, 0, 1.75], "h": 0.8},
    ]
else:
    objs = common + [
        {"type": "screen", "wall": "back", "u": 2.55, "v": 1.72, "w": 2.1, "h": 1.2},
        {"type": "projector", "pos": [2.55, H - 0.02, 1.9], "drop": 0.4},
        {"type": "desk", "pos": [3.55, 0, 0.5], "rotY": -20, "w": 0.95, "d": 0.5, "laptop": True, "books": True},
        {"type": "cubeShelf", "wall": "left", "u": 2.4, "cols": 4, "rows": 2, "fill": "books", "seed": 5},
        {"type": "plant", "pos": [3.85, 0, 1.6], "h": 1.0},
    ]
    for zi, z in enumerate([1.25, 1.95]):
        for xi, x in enumerate([1.5, 2.12, 2.74, 3.36]):
            objs.append({"type": "chair", "pos": [x, 0, z], "rotY": 180, "scale": 1.4,
                         "color": ["#1c7ed6", "#e64980", "#f59f00", "#2f9e44"][(xi + zi) % 4], "tablet": False})
if MODE == "entry":
    objs += [
        {"type": "counter", "pos": [2.42, 0, 6.3], "rotY": 0, "w": 1.45, "d": 0.55, "text": "WELCOME", "stripe": "#74c0fc"},
        {"type": "board", "kind": "notice", "wall": "right", "u": 7.6, "v": 1.55, "w": 1.1, "h": 0.8, "frame": 0.03, "frameColor": "#c8a165"},
        {"type": "shoeRack", "wall": "right", "u": 8.7, "n": 3, "cw": 0.34},
        {"type": "plant", "pos": [3.8, 0, 7.0], "h": 1.1, "pot": "#ffd43b"},
        {"type": "panelLight", "pos": [2.0, H, 6.5], "w": 0.6, "d": 0.6}, {"type": "panelLight", "pos": [2.0, H, 8.2], "w": 0.6, "d": 0.6},
        {"type": "bunting", "from": [0.02, 2.6, 4.6], "to": [W - 0.02, 2.6, 4.8], "sag": 0.3, "n": 15, "colors": ["#ff6b6b", "#ffd43b", "#69db7c", "#4dabf7", "#9775fa"]},
    ]
st.layer3d(objs, room, light, tag=MODE, occ=m_occ)
st.finish(f"hall_{MODE}", exposure=(0.97 if MODE == "entry" else 1.12), sat=1.06, contrast=1.03, vignette=0.1)
print("done", MODE)
