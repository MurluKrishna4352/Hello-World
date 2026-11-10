"""Compositing library for virtual staging of real frames (paint, decals, floor textures, 3D furniture layer)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import cv2
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from cam import Camera  # noqa: E402

OUT_W, OUT_H = 1080, 1440
S = 3.0  # source (360x480) -> output scale


# ---------------------------------------------------------------- colour helpers
def srgb2lin(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin2srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def hex2rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def lum(lin):
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


# ---------------------------------------------------------------- scene / camera
def load_scene(name):
    cfg = json.load(open(f"{BASE}/scenes/{name}.json"))
    camd = json.load(open(f"{BASE}/out/{name}_cam.json"))
    cam = Camera.from_json(camd)
    dims = camd.get("dims", {})
    return cfg, cam, dims


def ev(x, env):
    if isinstance(x, (int, float)):
        return float(x)
    return float(eval(str(x), {"__builtins__": {}}, env))


def src_frame(cfg):
    img = cv2.imread(cfg["frame"])
    return img


def enhance_source(img, bright=False, denoise=0):
    if bright:
        a = img.astype(np.float32) / 255
        p = np.percentile(a, 98)
        a = np.clip(a / p * 0.95, 0, 1) ** 0.62
        img = (a * 255).astype(np.uint8)
    if denoise:
        img = cv2.fastNlMeansDenoisingColored(img, None, denoise, denoise, 5, 15)
    return img


def upscale(img_bgr):
    big = cv2.resize(img_bgr, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(big, (0, 0), 2.0)
    big = cv2.addWeighted(big, 1.35, blur, -0.35, 0)
    return big


def to_float_rgb(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def to_bgr8(rgb):
    return cv2.cvtColor((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------- polygons + masks
def clip_poly_cam(cam, pts3d, near=0.08):
    """Project a planar 3D polygon, clipping against the camera near plane (Sutherland-Hodgman in camera space)."""
    P = np.asarray(pts3d, float)
    Xc = (cam.R @ P.T + cam.tvec).T
    out = []
    n = len(Xc)
    for i in range(n):
        a, b = Xc[i], Xc[(i + 1) % n]
        ina, inb = a[2] > near, b[2] > near
        if ina:
            out.append(a)
        if ina != inb:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    if len(out) < 3:
        return None
    out = np.array(out)
    uv = (cam.K @ out.T).T
    return uv[:, :2] / uv[:, 2:3]


def poly_mask(polys, size=(OUT_W, OUT_H), feather=1.2):
    m = np.zeros((size[1], size[0]), np.uint8)
    for p in polys:
        if p is None:
            continue
        cv2.fillPoly(m, [np.round(np.asarray(p) * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    m = m.astype(np.float32) / 255
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


def src_polys_to_out(polys):
    return [np.asarray(p, float) * S for p in polys]


# ---------------------------------------------------------------- shading
def shading_map(rgb, mask, strength=14, iters=2, detail=0.12, ref=None, gamma=1.0, clamp=(0.35, 1.8)):
    """Smoothed luminance relative to its median inside mask -> multiplicative shading for new paint."""
    lin = srgb2lin(rgb)
    Y = lum(lin)
    Y8 = (np.clip(Y ** (1 / 2.2), 0, 1) * 255).astype(np.uint8)
    Ys = Y8.copy()
    for _ in range(iters):
        Ys = cv2.bilateralFilter(Ys, 0, strength, 9)
    Ys = (Ys.astype(np.float32) / 255) ** 2.2
    sel = mask > 0.5
    r = np.median(Ys[sel]) if ref is None and sel.any() else (ref or 0.2)
    sh = (Ys / max(r, 1e-4)) ** gamma
    if detail:
        sh = sh * (1 + detail * (Y - Ys) / max(r, 1e-4))
    return np.clip(sh, *clamp), r


def paint(rgb, mask, color, shade=None, **kw):
    """Repaint masked region with `color` (hex or rgb 0..1) keeping real lighting."""
    if shade is None:
        shade, _ = shading_map(rgb, mask, **kw)
    c = hex2rgb(color) if isinstance(color, str) else np.asarray(color, np.float32)
    new = lin2srgb(srgb2lin(c)[None, None, :] * shade[..., None])
    m = mask[..., None]
    return rgb * (1 - m) + new * m


def warp_rgba(tex_rgba, Hm, size=(OUT_W, OUT_H)):
    t = tex_rgba.astype(np.float32) / 255
    # premultiply to avoid dark fringes
    t[..., :3] *= t[..., 3:4]
    w = cv2.warpPerspective(t, Hm, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    a = w[..., 3:4]
    rgb = np.where(a > 1e-4, w[..., :3] / np.maximum(a, 1e-4), 0)
    return rgb, a[..., 0]


def decal(rgb, tex_path_or_arr, cam, origin, u_axis, v_axis, metres, shade=None, opacity=1.0, clip_mask=None,
          shade_mix=1.0):
    """Paint a texture onto a world plane. origin = texture top-left in world; u/v axes unit vectors."""
    tex = cv2.imread(tex_path_or_arr, cv2.IMREAD_UNCHANGED) if isinstance(tex_path_or_arr, str) else tex_path_or_arr
    if tex.shape[2] == 3:
        tex = np.dstack([tex, np.full(tex.shape[:2], 255, np.uint8)])
    tex = cv2.cvtColor(tex, cv2.COLOR_BGRA2RGBA)
    # subdivide via homography (plane is planar, so one homography suffices as long as all corners in front)
    Hm = cam.plane_homography(origin, u_axis, v_axis, (tex.shape[1], tex.shape[0]), metres)
    col, a = warp_rgba(tex, Hm)
    a = a * opacity
    if clip_mask is not None:
        a = a * clip_mask
    if shade is not None:
        sh = 1 + (shade - 1) * shade_mix
        col = lin2srgb(srgb2lin(col) * sh[..., None])
    return rgb * (1 - a[..., None]) + col * a[..., None]


def over(rgb, layer_rgba):
    a = layer_rgba[..., 3:4]
    return rgb * (1 - a) + layer_rgba[..., :3] * a


def load_rgba(path, size=(OUT_W, OUT_H)):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
    if (im.shape[1], im.shape[0]) != size:
        # downsample with premultiplied alpha
        im[..., :3] *= im[..., 3:4]
        im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)
        a = im[..., 3:4]
        im[..., :3] = np.where(a > 1e-4, im[..., :3] / np.maximum(a, 1e-4), 0)
    return im


def grade(rgb, exposure=1.0, sat=1.0, warmth=0.0, vignette=0.0, contrast=1.0, lift=0.0):
    lin = srgb2lin(rgb) * exposure
    out = lin2srgb(lin)
    if contrast != 1.0:
        out = (out - 0.5) * contrast + 0.5
    if lift:
        out = out * (1 - lift) + lift
    if sat != 1.0:
        g = out.mean(-1, keepdims=True)
        out = g + (out - g) * sat
    if warmth:
        out = out * np.array([1 + warmth, 1 + warmth * 0.3, 1 - warmth], np.float32)
    if vignette:
        h, w = out.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.414
        out = out * (1 - vignette * r[..., None] ** 2)
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- 3D jobs
def make_job(name, cam, room, objects, light=None, tag="3d", scale=2.0, catchers=True):
    rc = cam.scaled(S * scale)
    job = {"width": rc.size[0], "height": rc.size[1], "camera": rc.threejs(), "room": room, "objects": objects,
           "light": light or {}, "catchers": catchers, "out": f"out/{name}_{tag}.png"}
    p = f"out/{name}_{tag}_job.json"
    json.dump(job, open(f"{BASE}/{p}", "w"))
    return p


def render_jobs(paths):
    r = subprocess.run(["node", f"{BASE}/web/render.js", *paths], cwd=BASE, capture_output=True, text=True, timeout=1800)
    print(r.stdout.strip())
    if r.returncode != 0 or "ERROR" in r.stdout or "pageerror" in r.stdout:
        print(r.stderr[-3000:])


def svg_to_png(svg_path, png_path, w, h):
    r = subprocess.run(["node", f"{BASE}/web/render.js", "--svg", svg_path, png_path, str(w), str(h)], cwd=BASE,
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(r.stdout, r.stderr[-2000:])


def inpaint_src(img_bgr, polys, radius=7):
    m = np.zeros(img_bgr.shape[:2], np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.asarray(p, np.int32)], 255)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(img_bgr, m, radius, cv2.INPAINT_TELEA)
