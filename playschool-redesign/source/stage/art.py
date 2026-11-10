"""SVG artwork generators (walls, murals, floors, signs). Units: metres, rendered at PX_PER_M."""
from __future__ import annotations

import math
import os

from stagelib import BASE, svg_to_png

PX = 300  # px per metre
FONT_CSS = """<style>
@font-face{font-family:Poppins;font-weight:700;src:url(/web/fonts/Poppins-Bold.ttf)}
@font-face{font-family:Poppins;font-weight:500;src:url(/web/fonts/Poppins-Medium.ttf)}
@font-face{font-family:Lora;font-weight:600;src:url(/web/fonts/Lora-Variable.ttf)}
html,body{margin:0;background:transparent}
</style>"""

RAINBOW = ['#ff6b6b', '#ffa94d', '#ffd43b', '#69db7c', '#4dabf7', '#9775fa']
SOFT_RAINBOW = ['#ff8787', '#ffc078', '#ffe066', '#8ce99a', '#74c0fc', '#b197fc']


class Svg:
    def __init__(self, w_m, h_m, px=PX):
        self.w, self.h, self.px = w_m, h_m, px
        self.parts = []

    def X(self, x):
        return x * self.px

    def Y(self, y):  # wall coords: y up from floor
        return (self.h - y) * self.px

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill, extra=""):
        self.add(f'<rect x="{self.X(x):.1f}" y="{self.Y(y + h):.1f}" width="{w * self.px:.1f}" height="{h * self.px:.1f}" fill="{fill}" {extra}/>')

    def circle(self, x, y, r, fill, extra=""):
        self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r * self.px:.1f}" fill="{fill}" {extra}/>')

    def text(self, x, y, s, size, fill, weight=700, anchor="middle", family="Poppins", extra=""):
        self.add(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-family="{family}" font-weight="{weight}" '
                 f'font-size="{size * self.px:.1f}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')

    def svg(self):
        W, H = round(self.w * self.px), round(self.h * self.px)
        return (f'<!doctype html><html><head><meta charset="utf-8">{FONT_CSS}</head><body>'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                + "".join(self.parts) + "</svg></body></html>")

    def render(self, name):
        os.makedirs(f"{BASE}/art", exist_ok=True)
        hp = f"{BASE}/art/{name}.html"
        open(hp, "w").write(self.svg())
        out = f"{BASE}/art/{name}.png"
        svg_to_png(hp, out, round(self.w * self.px), round(self.h * self.px))
        return out


# ---------------------------------------------------------------- reusable motifs
def scallop_dado(s: Svg, x0, x1, top, base_col, edge_col="#ffffff", r=0.07):
    s.rect(x0, 0, x1 - x0, top, base_col)
    n = int(math.ceil((x1 - x0) / (2 * r)))
    d = f'M{s.X(x0):.1f},{s.Y(top):.1f} '
    for i in range(n):
        cx = x0 + r + i * 2 * r
        d += f'A{r * s.px:.1f},{r * s.px:.1f} 0 0 1 {s.X(cx + r):.1f},{s.Y(top):.1f} '
    s.add(f'<path d="{d}" fill="{base_col}" stroke="{edge_col}" stroke-width="{0.022 * s.px:.1f}"/>')
    s.add(f'<line x1="{s.X(x0)}" y1="{s.Y(top) + 0.011 * s.px}" x2="{s.X(x1)}" y2="{s.Y(top) + 0.011 * s.px}" stroke="{base_col}" stroke-width="{0.02 * s.px}"/>')


def cloud(s: Svg, x, y, k=1.0, fill="#ffffff", stroke="#d0ebff"):
    parts = [(0, 0, 0.16), (0.17, -0.03, 0.12), (-0.17, -0.04, 0.11), (0.07, 0.08, 0.12), (-0.08, 0.06, 0.1)]
    g = "".join(f'<circle cx="{s.X(x + dx * k):.1f}" cy="{s.Y(y + dy * k):.1f}" r="{r * k * s.px:.1f}"/>' for dx, dy, r in parts)
    s.add(f'<g fill="{fill}" stroke="{stroke}" stroke-width="{0.012 * s.px:.1f}">{g}</g><g fill="{fill}">{g}</g>')
    s.rect(x - 0.25 * k, y - 0.15 * k, 0.5 * k, 0.1 * k, fill)


def sun(s: Svg, x, y, r=0.18, face=True):
    rays = "".join(
        f'<line x1="{s.X(x + math.cos(a) * r * 1.25):.1f}" y1="{s.Y(y + math.sin(a) * r * 1.25):.1f}" '
        f'x2="{s.X(x + math.cos(a) * r * 1.6):.1f}" y2="{s.Y(y + math.sin(a) * r * 1.6):.1f}"/>'
        for a in [i * math.pi / 6 for i in range(12)])
    s.add(f'<g stroke="#fcc419" stroke-width="{0.03 * s.px:.1f}" stroke-linecap="round">{rays}</g>')
    s.circle(x, y, r, "#ffd43b", f'stroke="#fab005" stroke-width="{0.015 * s.px:.1f}"')
    if face:
        s.circle(x - r * 0.33, y + r * 0.15, r * 0.09, "#5c3d00")
        s.circle(x + r * 0.33, y + r * 0.15, r * 0.09, "#5c3d00")
        s.add(f'<path d="M{s.X(x - r * 0.4):.1f},{s.Y(y - r * 0.2):.1f} Q{s.X(x):.1f},{s.Y(y - r * 0.6):.1f} {s.X(x + r * 0.4):.1f},{s.Y(y - r * 0.2):.1f}" '
              f'fill="none" stroke="#5c3d00" stroke-width="{0.018 * s.px:.1f}" stroke-linecap="round"/>')
        s.circle(x - r * 0.55, y - r * 0.15, r * 0.12, "#ff8787", 'opacity="0.6"')
        s.circle(x + r * 0.55, y - r * 0.15, r * 0.12, "#ff8787", 'opacity="0.6"')


def rainbow_arc(s: Svg, cx, cy, r_out, band, colors=SOFT_RAINBOW, legs=0.0):
    for i, c in enumerate(colors):
        r = r_out - band * (i + 0.5)
        d = f'M{s.X(cx - r):.1f},{s.Y(cy - legs):.1f} L{s.X(cx - r):.1f},{s.Y(cy):.1f} A{r * s.px:.1f},{r * s.px:.1f} 0 0 1 {s.X(cx + r):.1f},{s.Y(cy):.1f} L{s.X(cx + r):.1f},{s.Y(cy - legs):.1f}'
        s.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{band * s.px + 1:.1f}"/>')


def hill(s: Svg, x0, x1, base, peak, col):
    xm = (x0 + x1) / 2
    s.add(f'<path d="M{s.X(x0):.1f},{s.Y(base):.1f} C{s.X(x0 + (xm - x0) * 0.5):.1f},{s.Y(peak):.1f} {s.X(xm + (x1 - xm) * 0.5):.1f},{s.Y(peak):.1f} {s.X(x1):.1f},{s.Y(base):.1f} Z" fill="{col}"/>')


def tree(s: Svg, x, y, h=0.45, col="#2f9e44", fruit=True):
    s.rect(x - 0.025, y, 0.05, h * 0.45, "#a0522d")
    s.circle(x, y + h * 0.62, h * 0.33, col)
    s.circle(x - h * 0.17, y + h * 0.52, h * 0.22, col)
    s.circle(x + h * 0.18, y + h * 0.55, h * 0.22, col)
    if fruit:
        for dx, dy in [(-0.1, 0.65), (0.08, 0.75), (0.12, 0.5), (-0.03, 0.85)]:
            s.circle(x + dx * h, y + dy * h, 0.022, "#ff6b6b")


def bird(s: Svg, x, y, k=1.0, col="#495057"):
    s.add(f'<path d="M{s.X(x - 0.06 * k):.1f},{s.Y(y + 0.02 * k):.1f} Q{s.X(x - 0.03 * k):.1f},{s.Y(y + 0.04 * k):.1f} {s.X(x):.1f},{s.Y(y):.1f} '
          f'Q{s.X(x + 0.03 * k):.1f},{s.Y(y + 0.04 * k):.1f} {s.X(x + 0.06 * k):.1f},{s.Y(y + 0.02 * k):.1f}" fill="none" stroke="{col}" stroke-width="{0.012 * s.px:.1f}" stroke-linecap="round"/>')


def flower(s: Svg, x, y, r=0.05, col="#f783ac", stem=0.18):
    s.add(f'<line x1="{s.X(x):.1f}" y1="{s.Y(y):.1f}" x2="{s.X(x):.1f}" y2="{s.Y(y - stem):.1f}" stroke="#2f9e44" stroke-width="{0.014 * s.px:.1f}"/>')
    for i in range(6):
        a = i * math.pi / 3
        s.circle(x + math.cos(a) * r, y + math.sin(a) * r, r * 0.62, col)
    s.circle(x, y, r * 0.55, "#ffd43b")


def butterfly(s: Svg, x, y, k=1.0, c1="#9775fa", c2="#f783ac"):
    for sx in (-1, 1):
        s.add(f'<ellipse cx="{s.X(x + sx * 0.04 * k):.1f}" cy="{s.Y(y + 0.03 * k):.1f}" rx="{0.04 * k * s.px:.1f}" ry="{0.05 * k * s.px:.1f}" fill="{c1}"/>')
        s.add(f'<ellipse cx="{s.X(x + sx * 0.035 * k):.1f}" cy="{s.Y(y - 0.035 * k):.1f}" rx="{0.03 * k * s.px:.1f}" ry="{0.035 * k * s.px:.1f}" fill="{c2}"/>')
    s.rect(x - 0.008 * k, y - 0.06 * k, 0.016 * k, 0.12 * k, "#343a40", f'rx="{0.008 * k * s.px:.1f}"')


def letters(s: Svg, x, y, txt, size, colors=RAINBOW, gap=0.0, family="Poppins", stroke=None):
    # approximate advance for Poppins bold
    cw = size * 0.68
    total = len(txt) * cw + gap * (len(txt) - 1)
    cx = x - total / 2
    for i, ch in enumerate(txt):
        if ch != " ":
            st = f'stroke="{stroke}" stroke-width="{0.012 * s.px:.1f}" paint-order="stroke"' if stroke else ""
            s.text(cx + cw / 2, y, ch, size, colors[i % len(colors)], extra=st, family=family)
        cx += cw + gap


def train(s: Svg, x0, y0, cars, h=0.32, colors=RAINBOW):
    """Alphabet/number train running left->right, engine at the right end."""
    cw = h * 1.25
    x = x0
    for i, label in enumerate(cars):
        c = colors[i % len(colors)]
        s.rect(x, y0 + 0.06, cw, h, c, f'rx="{0.03 * s.px}"')
        s.rect(x + cw * 0.12, y0 + 0.06 + h * 0.18, cw * 0.76, h * 0.68, "#ffffff", f'rx="{0.025 * s.px}"')
        s.text(x + cw / 2, y0 + 0.06 + h * 0.3, label, h * 0.55, c)
        for wx in (x + cw * 0.25, x + cw * 0.75):
            s.circle(wx, y0 + 0.05, 0.05, "#343a40")
            s.circle(wx, y0 + 0.05, 0.02, "#ced4da")
        if i:
            s.rect(x - 0.06, y0 + 0.1, 0.06, 0.025, "#495057")
        x += cw + 0.06
    # engine
    s.rect(x, y0 + 0.06, cw * 1.35, h * 0.85, "#e03131", f'rx="{0.03 * s.px}"')
    s.rect(x + cw * 0.1, y0 + 0.06 + h * 0.85, cw * 0.55, h * 0.55, "#c92a2a", f'rx="{0.02 * s.px}"')
    s.rect(x + cw * 0.18, y0 + 0.06 + h * 0.95, cw * 0.38, h * 0.32, "#a5d8ff", f'rx="{0.015 * s.px}"')
    s.rect(x + cw * 0.95, y0 + 0.06 + h * 0.85, cw * 0.18, h * 0.45, "#343a40")
    s.add(f'<rect x="{s.X(x - 0.06):.1f}" y="{s.Y(y0 + 0.125):.1f}" width="{0.06 * s.px:.1f}" height="{0.025 * s.px:.1f}" fill="#495057"/>')
    for wx, r in ((x + cw * 0.3, 0.07), (x + cw * 1.05, 0.05)):
        s.circle(wx, y0 + 0.06, r, "#343a40")
        s.circle(wx, y0 + 0.06, r * 0.4, "#ced4da")
    for i, (dx, dy, r) in enumerate([(1.05, 1.5, 0.05), (1.15, 1.75, 0.065), (1.3, 2.0, 0.08)]):
        s.circle(x + cw * dx, y0 + h * dy, r, "#e9ecef", 'opacity="0.95"')
    # track
    s.rect(x0 - 0.05, y0 - 0.01, x + cw * 1.4 - x0 + 0.1, 0.02, "#868e96")


def footprint(s: Svg, x, y, k=0.1, col="#ff8787", rot=0, mirror=False):
    m = -1 if mirror else 1
    g = (f'<g transform="translate({s.X(x):.1f},{s.Y(y):.1f}) rotate({rot}) scale({m},1)">'
         f'<ellipse cx="0" cy="{0.03 * s.px:.1f}" rx="{k * 0.35 * s.px:.1f}" ry="{k * 0.6 * s.px:.1f}" fill="{col}"/>')
    for i, (tx, ty, tr) in enumerate([(-0.025, -0.075, 0.018), (-0.005, -0.085, 0.015), (0.013, -0.08, 0.013), (0.028, -0.07, 0.011), (0.038, -0.055, 0.01)]):
        g += f'<circle cx="{tx * s.px * k / 0.1:.1f}" cy="{(ty * k / 0.1 - 0.0) * s.px:.1f}" r="{tr * s.px * k / 0.1:.1f}" fill="{col}"/>'
    s.add(g + "</g>")


def sprout_logo(s: Svg, x, y, k=1.0):
    """Small sprout-in-a-sun logo centred at (x, y)."""
    s.circle(x, y, 0.2 * k, "#ffd43b")
    s.add(f'<path d="M{s.X(x):.1f},{s.Y(y - 0.13 * k):.1f} L{s.X(x):.1f},{s.Y(y + 0.02 * k):.1f}" stroke="#2f9e44" stroke-width="{0.025 * k * s.px:.1f}" stroke-linecap="round"/>')
    s.add(f'<path d="M{s.X(x):.1f},{s.Y(y + 0.0 * k):.1f} C{s.X(x - 0.02 * k):.1f},{s.Y(y + 0.12 * k):.1f} {s.X(x - 0.13 * k):.1f},{s.Y(y + 0.12 * k):.1f} {s.X(x - 0.15 * k):.1f},{s.Y(y + 0.07 * k):.1f} C{s.X(x - 0.1 * k):.1f},{s.Y(y + 0.0 * k):.1f} {s.X(x - 0.03 * k):.1f},{s.Y(y - 0.01 * k):.1f} {s.X(x):.1f},{s.Y(y + 0.0 * k):.1f}Z" fill="#51cf66"/>')
    s.add(f'<path d="M{s.X(x):.1f},{s.Y(y + 0.02 * k):.1f} C{s.X(x + 0.02 * k):.1f},{s.Y(y + 0.15 * k):.1f} {s.X(x + 0.14 * k):.1f},{s.Y(y + 0.15 * k):.1f} {s.X(x + 0.16 * k):.1f},{s.Y(y + 0.1 * k):.1f} C{s.X(x + 0.1 * k):.1f},{s.Y(y + 0.02 * k):.1f} {s.X(x + 0.03 * k):.1f},{s.Y(y + 0.01 * k):.1f} {s.X(x):.1f},{s.Y(y + 0.02 * k):.1f}Z" fill="#37b24d"/>')
