"""Montessori artwork: calm natural palette, wood, prints, floors, exterior cladding and signage (SVG, metres)."""
from __future__ import annotations

import math
import random

from art import Svg

WARM_WHITE = "#f6f1e7"
LINEN = "#efe6d6"
SAGE = "#9aab88"
SAGE_D = "#6f8160"
TERRA = "#c27a56"
OAK = "#d3ad80"
OAK_D = "#a57b4f"
INK = "#3d3a36"
MONTE_CONT = {"asia": "#e9c03a", "africa": "#4f9a46", "europe": "#d64535", "namerica": "#ef8a2a",
              "samerica": "#e06a9a", "australia": "#8a5a33", "antarctica": "#f4f4f4"}


def wainscot(s: Svg, x0, x1, top=0.92, panel=0.6, base=OAK, rail=OAK_D):
    s.rect(x0, 0, x1 - x0, top, base)
    rnd = random.Random(3)
    # vertical tongue-and-groove boards
    x = x0
    while x < x1:
        w = 0.12
        shade = rnd.uniform(-0.04, 0.04)
        col = _mix(base, "#000000" if shade < 0 else "#ffffff", abs(shade))
        s.rect(x, 0.1, min(w, x1 - x), top - 0.1, col)
        s.add(f'<line x1="{s.X(x):.1f}" y1="{s.Y(0.1):.1f}" x2="{s.X(x):.1f}" y2="{s.Y(top):.1f}" stroke="{rail}" stroke-width="2" opacity="0.6"/>')
        x += w
    s.rect(x0, top - 0.04, x1 - x0, 0.05, rail)               # top rail
    s.rect(x0, top + 0.01, x1 - x0, 0.012, "#8a6440")
    s.rect(x0, 0, x1 - x0, 0.1, _mix(rail, "#000000", 0.1))  # skirting


def _mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * (1 - t) + y * t):02x}" for x, y in zip(a, b))


def framed_print(s: Svg, x, y, w, h, variant="leaf", caption=""):
    """x, y = bottom-left on the wall."""
    s.rect(x - 0.025, y - 0.025, w + 0.05, h + 0.05, OAK_D, f'rx="{0.006 * s.px}"')
    s.rect(x, y, w, h, "#fbf7ef")
    cx, cy = x + w / 2, y + h * 0.55
    if variant == "leaf":
        r = min(w, h) * 0.38
        s.add(f'<path d="M{s.X(cx):.1f},{s.Y(cy - r):.1f} C{s.X(cx - r):.1f},{s.Y(cy - r * 0.3):.1f} {s.X(cx - r * 0.6):.1f},{s.Y(cy + r * 0.8):.1f} '
              f'{s.X(cx):.1f},{s.Y(cy + r):.1f} C{s.X(cx + r * 0.6):.1f},{s.Y(cy + r * 0.8):.1f} {s.X(cx + r):.1f},{s.Y(cy - r * 0.3):.1f} '
              f'{s.X(cx):.1f},{s.Y(cy - r):.1f}Z" fill="{SAGE}"/>')
        s.add(f'<line x1="{s.X(cx):.1f}" y1="{s.Y(cy - r):.1f}" x2="{s.X(cx):.1f}" y2="{s.Y(cy + r * 0.9):.1f}" stroke="#fbf7ef" stroke-width="{0.006 * s.px:.1f}"/>')
    elif variant == "bird":
        s.add(f'<ellipse cx="{s.X(cx):.1f}" cy="{s.Y(cy):.1f}" rx="{w * 0.26 * s.px:.1f}" ry="{h * 0.16 * s.px:.1f}" fill="{TERRA}" transform="rotate(-18 {s.X(cx):.1f} {s.Y(cy):.1f})"/>')
        s.circle(cx + w * 0.2, cy + h * 0.13, w * 0.1, TERRA)
        s.circle(cx + w * 0.23, cy + h * 0.15, w * 0.018, INK)
        s.add(f'<line x1="{s.X(x + w * 0.12):.1f}" y1="{s.Y(cy - h * 0.2):.1f}" x2="{s.X(x + w * 0.88):.1f}" y2="{s.Y(cy - h * 0.22):.1f}" stroke="{OAK_D}" stroke-width="{0.008 * s.px:.1f}"/>')
    elif variant == "tree":
        s.rect(cx - w * 0.03, y + h * 0.15, w * 0.06, h * 0.35, OAK_D)
        s.circle(cx, cy + h * 0.08, w * 0.27, SAGE)
        s.circle(cx - w * 0.1, cy + h * 0.14, w * 0.13, "#b5c4a3")
    elif variant == "sun":
        s.circle(cx, cy, w * 0.2, "#e2b25a")
        s.add(f'<path d="M{s.X(x + w * 0.1):.1f},{s.Y(y + h * 0.2):.1f} Q{s.X(cx):.1f},{s.Y(y + h * 0.42):.1f} {s.X(x + w * 0.9):.1f},{s.Y(y + h * 0.2):.1f}" stroke="{SAGE_D}" fill="none" stroke-width="{0.01 * s.px:.1f}"/>')
    if caption:
        s.text(cx, y + h * 0.06, caption, h * 0.075, "#6b625a", weight=600, family="Lora")


def quote(s: Svg, cx, y, text, author, size=0.11):
    s.text(cx, y, f"“{text}”", size, INK, weight=600, family="Lora", extra='font-style="italic"')
    s.text(cx, y - size * 1.05, f"— {author}", size * 0.5, SAGE_D, weight=500)


def world_map(s: Svg, x, y, w, h):
    s.rect(x - 0.03, y - 0.03, w + 0.06, h + 0.06, OAK_D, f'rx="{0.008 * s.px}"')
    s.rect(x, y, w, h, "#cfe4ef")
    blobs = [("namerica", 0.2, 0.68, 0.14, 0.17), ("samerica", 0.3, 0.32, 0.07, 0.16), ("europe", 0.5, 0.72, 0.06, 0.07),
             ("africa", 0.52, 0.45, 0.09, 0.16), ("asia", 0.72, 0.68, 0.18, 0.16), ("australia", 0.84, 0.3, 0.07, 0.06),
             ("antarctica", 0.5, 0.06, 0.3, 0.035)]
    for k, bx, by, rx, ry in blobs:
        cx, cy = x + bx * w, y + by * h
        pts = []
        rr = random.Random(hash(k) % 1000)
        for i in range(14):
            a = i / 14 * 2 * math.pi
            f = 0.75 + 0.35 * rr.random()
            pts.append(f"{s.X(cx + math.cos(a) * rx * w * f):.1f},{s.Y(cy + math.sin(a) * ry * h * f):.1f}")
        s.add(f'<polygon points="{" ".join(pts)}" fill="{MONTE_CONT[k]}" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>')


def oak_floor(w, h, name, x_off=0.0):
    """Floor texture (rows = +z). Planks run along z (towards the camera)."""
    s = Svg(w, h)
    rnd = random.Random(11)
    P = s.px
    pw = 0.16
    x = 0
    while x < w:
        z = -rnd.uniform(0, 1.2)
        while z < h:
            L = rnd.uniform(0.9, 1.8)
            base = rnd.choice(["#d9b78c", "#d2ad80", "#ddbd93", "#cfa979", "#d6b386"])
            s.add(f'<rect x="{x * P:.1f}" y="{z * P:.1f}" width="{pw * P:.1f}" height="{L * P:.1f}" fill="{base}" stroke="#a9845a" stroke-width="1.6"/>')
            for g in range(3):
                gx = x + rnd.uniform(0.02, pw - 0.02)
                s.add(f'<line x1="{gx * P:.1f}" y1="{z * P:.1f}" x2="{(gx + rnd.uniform(-0.01, 0.01)) * P:.1f}" y2="{(z + L) * P:.1f}" '
                      f'stroke="#b8925f" stroke-width="1" opacity="0.35"/>')
            z += L
        x += pw
    return s.render(name)


def ellipse_line(w, h, cx, cz, a, b, name, col="#fbf7ef"):
    s = Svg(w, h)
    P = s.px
    s.add(f'<ellipse cx="{cx * P:.1f}" cy="{cz * P:.1f}" rx="{a * P:.1f}" ry="{b * P:.1f}" fill="none" stroke="{col}" stroke-width="{0.05 * P:.1f}"/>')
    return s.render(name)


def wood_slats(s: Svg, x0, x1, y0, y1, slat=0.05, gap=0.012):
    s.rect(x0, y0, x1 - x0, y1 - y0, "#7a5a3a")
    rnd = random.Random(5)
    x = x0 + gap / 2
    while x < x1 - 0.005:
        col = rnd.choice(["#c99a68", "#c4945f", "#cfa271", "#c08d58"])
        s.rect(x, y0, min(slat, x1 - x), y1 - y0, col)
        s.add(f'<line x1="{s.X(x + slat * 0.85):.1f}" y1="{s.Y(y0):.1f}" x2="{s.X(x + slat * 0.85):.1f}" y2="{s.Y(y1):.1f}" stroke="#a87a4a" stroke-width="2" opacity="0.6"/>')
        x += slat + gap


def green_wall(s: Svg, x0, x1, y0, y1):
    s.rect(x0, y0, x1 - x0, y1 - y0, "#3f5e34")
    rnd = random.Random(8)
    for _ in range(int((x1 - x0) * (y1 - y0) * 900)):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(0.018, 0.04)
        col = rnd.choice(["#5e8a4a", "#6f9a55", "#4f7a3e", "#86ad68", "#3f6a33"])
        ang = rnd.uniform(0, 180)
        s.add(f'<ellipse cx="{s.X(cx):.1f}" cy="{s.Y(cy):.1f}" rx="{r * s.px:.1f}" ry="{r * 0.45 * s.px:.1f}" fill="{col}" '
              f'transform="rotate({ang:.0f} {s.X(cx):.1f} {s.Y(cy):.1f})"/>')
    s.rect(x0 - 0.015, y0 - 0.015, x1 - x0 + 0.03, 0.03, OAK_D)
    s.rect(x0 - 0.015, y1 - 0.015, x1 - x0 + 0.03, 0.03, OAK_D)


def leaf_logo(s: Svg, x, y, k=1.0, col=SAGE_D):
    s.circle(x, y, 0.19 * k, "#f3ead9", f'stroke="{col}" stroke-width="{0.012 * k * s.px:.1f}"')
    for ang, c in ((-35, col), (35, "#8fa57c")):
        s.add(f'<ellipse cx="{s.X(x):.1f}" cy="{s.Y(y + 0.05 * k):.1f}" rx="{0.05 * k * s.px:.1f}" ry="{0.11 * k * s.px:.1f}" fill="{c}" '
              f'transform="rotate({ang} {s.X(x):.1f} {s.Y(y - 0.03 * k):.1f})"/>')
    s.add(f'<line x1="{s.X(x):.1f}" y1="{s.Y(y - 0.12 * k):.1f}" x2="{s.X(x):.1f}" y2="{s.Y(y + 0.02 * k):.1f}" stroke="{col}" stroke-width="{0.016 * k * s.px:.1f}" stroke-linecap="round"/>')
