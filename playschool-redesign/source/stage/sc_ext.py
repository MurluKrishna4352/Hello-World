"""Exterior: front door close-up and full facade (same world: origin = bottom-left of the door, facade plane z=0)."""
import sys

import numpy as np

from art import RAINBOW, SOFT_RAINBOW, Svg, cloud, flower, letters, sprout_logo, sun
from scenekit import Stage, hue_gate

SCHOOL = "Little Sprouts"
WHICH = sys.argv[1] if len(sys.argv) > 1 else "door"
FX0, FX1, FH = -0.65, 2.95, 2.05     # facade extents (world x) and painted height
WALL, PLINTH = "#c5e6ff", "#339af0"


def facade_art():
    s = Svg(FX1 - FX0, FH)
    L = lambda x: x - FX0
    s.rect(0, 0, FX1 - FX0, FH, WALL)
    # soft clouds high on the wall
    cloud(s, L(2.45), 1.98, 0.35)
    # rainbow door surround (sides + top band)
    for i, c in enumerate(RAINBOW[:5]):
        s.rect(L(-0.32 + i * 0.064), 0, 0.064, FH, c)
        s.rect(L(1.0 + (4 - i) * 0.064), 0, 0.064, FH, c)
        s.rect(L(-0.32), 1.93 + (4 - i) * 0.03, 1.64, 0.03, c)
    # giant crayon on the narrow wall left of the door
    cx0, cx1 = L(-0.55), L(-0.34)
    s.add(f'<path d="M{s.X(cx0):.1f},{s.Y(0.4):.1f} L{s.X(cx0):.1f},{s.Y(1.55):.1f} L{s.X((cx0 + cx1) / 2):.1f},{s.Y(1.86):.1f} '
          f'L{s.X(cx1):.1f},{s.Y(1.55):.1f} L{s.X(cx1):.1f},{s.Y(0.4):.1f} Z" fill="#ff922b"/>')
    s.rect(cx0, 1.42, cx1 - cx0, 0.06, "#e8590c")
    s.rect(cx0, 0.52, cx1 - cx0, 0.06, "#e8590c")
    s.add(f'<path d="M{s.X(cx0 + 0.07):.1f},{s.Y(1.76):.1f} L{s.X((cx0 + cx1) / 2):.1f},{s.Y(1.86):.1f} L{s.X(cx1 - 0.07):.1f},{s.Y(1.76):.1f} Z" fill="#5c3d00"/>')
    # plinth with handprints
    s.rect(0, 0, FX1 - FX0, 0.32, PLINTH)
    s.rect(0, 0.32, FX1 - FX0, 0.025, "#ffffff")
    for i, x in enumerate(np.arange(1.45, 2.9, 0.28)):
        s.circle(L(x), 0.16, 0.055, ["#ffd43b", "#ff8787", "#8ce99a", "#ffffff", "#b197fc"][i % 5])
    # timings board under the window
    bx0, bx1, by0, by1 = L(1.42), L(2.86), 0.38, 0.8
    s.rect(bx0, by0, bx1 - bx0, by1 - by0, "#ffffff", f'rx="{0.03 * s.px}" stroke="#1c7ed6" stroke-width="{0.02 * s.px}"')
    s.text((bx0 + bx1) / 2, 0.69, "ADMISSIONS OPEN", 0.07, "#e03131")
    s.text((bx0 + bx1) / 2, 0.57, "Play School  9 AM – 1 PM", 0.058, "#1c7ed6", weight=500)
    s.text((bx0 + bx1) / 2, 0.46, "Teacher Training  2 – 5 PM", 0.058, "#2b8a3e", weight=500)
    return s.render("facade")


def sign_art():
    s = Svg(3.22, 0.6)
    s.rect(0, 0, 3.22, 0.6, "#ffffff")
    for i, c in enumerate(RAINBOW):
        s.rect(0, 0.6 - 0.018 * (i + 1), 3.22, 0.018, c)
    sprout_logo(s, 0.33, 0.29, 1.15)
    letters(s, 1.8, 0.27, SCHOOL, 0.25, ["#e03131", "#f08c00", "#2f9e44", "#1971c2", "#9c36b5", "#e64980"], gap=-0.035)
    s.text(1.8, 0.075, "PLAY SCHOOL  &amp;  TEACHER TRAINING CENTRE", 0.075, "#1864ab", weight=700)
    return s.render("sign")


def banner_art(kind):
    if kind == 1:
        s = Svg(3.8, 0.5)
        s.rect(0, 0, 3.8, 0.5, "#fa5252")
        s.rect(0.08, 0.06, 1.35, 0.38, "#ffffff", f'rx="{0.05 * s.px}"')
        s.text(0.755, 0.175, "PLAY SCHOOL", 0.15, "#e03131")
        s.text(2.6, 0.27, "Playgroup • Nursery • LKG • UKG", 0.115, "#ffffff", weight=700)
        s.text(2.6, 0.1, "Classrooms on this floor", 0.08, "#fff3bf", weight=500)
    else:
        s = Svg(3.2, 0.5)
        s.rect(0, 0, 3.2, 0.5, "#1c7ed6")
        s.text(1.6, 0.26, "TEACHER TRAINING CENTRE", 0.15, "#ffffff")
        s.text(1.6, 0.09, "NTT  •  ECCE  •  Workshops", 0.085, "#ffe066", weight=500)
    return s.render(f"banner{kind}")


def hopscotch_art():
    # floor texture: x -0.6..2.9 (u), z 0.1..1.1 (v, rows increase towards the street)
    s = Svg(3.5, 1.0)
    P = s.px
    cells = [(1.62, 0.5, "1"), (1.92, 0.5, "2"), (2.22, 0.35, "3"), (2.22, 0.65, "4"), (2.52, 0.5, "5"), (2.82, 0.35, "6"), (2.82, 0.65, "7")]
    for i, (x, z, n) in enumerate(cells):
        X, Z = (x - 0.15 + 0.6) * P, (z - 0.15 - 0.1) * P
        c = RAINBOW[i % 6]
        s.add(f'<rect x="{X:.1f}" y="{Z:.1f}" width="{0.3 * P:.1f}" height="{0.3 * P:.1f}" fill="none" stroke="{c}" stroke-width="{0.03 * P:.1f}"/>')
        s.add(f'<text x="{X + 0.15 * P:.1f}" y="{Z + 0.2 * P:.1f}" font-family="Poppins" font-weight="700" font-size="{0.14 * P:.1f}" '
              f'fill="{c}" text-anchor="middle">{n}</text>')
    return s.render("hopscotch")


facade, sign, hop = facade_art(), sign_art(), hopscotch_art()
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

sh_wall, _ = st.shading(st.gate(m_wall, lmin=0.1), strength=10, iters=1, detail=0.35, clamp=(0.45, 1.5))
st.texture(facade, [FX0, FH, 0], [1, 0, 0], [0, -1, 0], (FX1 - FX0, FH), mask=m_wall, shade=sh_wall)

# soffit / beam underside painted white
m_sof = st.mask(include_src=soffit_src)
yy = np.linspace(0.78, 0.95, m_sof.shape[0])[:, None] * np.ones((1, m_sof.shape[1]))
st.paint(m_sof, "#f1f3f5", yy.astype(np.float32))

# door: black grille -> sunshine yellow (keep the grille relief)
m_door = st.mask([door], feather=0.8)
sh_door, _ = st.shading(m_door, strength=6, iters=1, detail=0.6, gamma=0.85, clamp=(0.22, 2.0))
st.paint(m_door, "#f2a900", sh_door)

if WHICH == "door":
    m_ground = st.mask([[[FX0, 0, 0.05], [FX1, 0, 0.05], [FX1, 0, 1.1], [FX0, 0, 1.1]]])
    sh_g, _ = st.shading(m_ground, strength=10, iters=1, detail=0.2)
    st.texture(hop, [-0.6, 0, 0.1], [1, 0, 0], [0, 0, 1], (3.5, 1.0), mask=m_ground, shade=sh_g, opacity=0.95)
else:
    # upper floors: vinyl banners on the balcony railings
    st.quad_texture(b1, [(70, 193), (300, 195), (300, 221), (70, 220)])
    st.quad_texture(b2, [(112, 113), (258, 114), (258, 135), (112, 134)])

room = {"W": 3.8, "H": 2.6, "D": 3.0, "z0": 0, "x0": -0.7, "noLeft": True, "noRight": True}
light = {"dir": [0.9, 1.1, 0.9], "sun": 2.2, "hemi": 1.3, "ambient": 0.3, "shadowOpacity": 0.42, "shadowRadius": 5,
         "sky": "#eaf4ff"}
objs = [
    {"type": "signBox", "wall": "back", "u": 1.06, "v": 2.33, "w": 3.22, "h": 0.6, "t": 0.07, "src": "/art/sign.png",
     "edge": "#1c7ed6", "glow": 0.25},
    {"type": "planter", "pos": [-0.42, 0, 0.28], "w": 0.36, "h": 0.42, "d": 0.32, "color": "#ff6b6b", "flowers": True, "seed": 4},
    {"type": "planter", "pos": [1.28, 0, 0.26], "w": 0.36, "h": 0.42, "d": 0.32, "color": "#69db7c", "flowers": True, "seed": 9},
    {"type": "rug", "pos": [0.5, 0, 0.32], "w": 0.95, "d": 0.5, "style": "plain", "color": "#ffd43b", "border": "#ff6b6b"},
]
st.layer3d(objs, room, light, tag="ext")
st.finish(WHICH, exposure=1.05, sat=1.06, contrast=1.02, vignette=0.08)
print("done", WHICH)
