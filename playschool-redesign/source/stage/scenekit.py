"""High-level staging helper used by every scene script."""
from __future__ import annotations

import os

import cv2
import numpy as np

from stagelib import (BASE, OUT_H, OUT_W, S, clip_poly_cam, decal, enhance_source, grade, inpaint_src, lin2srgb,
                      load_rgba, load_scene, make_job, over, poly_mask, render_jobs, shading_map, src_frame, srgb2lin,
                      to_bgr8, to_float_rgb, upscale, hex2rgb, lum)

OUT = f"{BASE}/final"
os.makedirs(OUT, exist_ok=True)


def arch_poly(cx, spring, r, x_l=None, x_r=None, bottom=-0.05, n=24, z=0.0):
    x_l = cx - r if x_l is None else x_l
    x_r = cx + r if x_r is None else x_r
    pts = [[x_l, bottom, z]]
    for i in range(n + 1):
        a = np.pi - i * np.pi / n
        pts.append([cx + np.cos(a) * r, spring + np.sin(a) * r, z])
    pts.append([x_r, bottom, z])
    return pts


class Stage:
    def __init__(self, name, bright=False, denoise=0, inpaint=None, src_override=None):
        self.name = name
        self.cfg, cam, self.dims = load_scene(name)
        raw = src_frame(self.cfg) if src_override is None else src_override
        self.before = to_float_rgb(upscale(enhance_source(raw.copy(), bright, denoise)))
        src = inpaint_src(raw.copy(), inpaint) if inpaint else raw.copy()
        self.base = to_float_rgb(upscale(enhance_source(src, bright, denoise)))
        self.cam = cam.scaled(S)
        self.img = self.base.copy()
        self.lin = srgb2lin(self.base)

    # ------------------------------------------------------------ geometry
    def proj_poly(self, pts3d):
        return clip_poly_cam(self.cam, pts3d)

    def mask(self, include=(), exclude=(), include_src=(), exclude_src=(), feather=1.0):
        inc = [self.proj_poly(p) for p in include] + [np.asarray(p, float) * S for p in include_src]
        m = poly_mask(inc, feather=feather)
        ex = [self.proj_poly(p) for p in exclude] + [np.asarray(p, float) * S for p in exclude_src]
        if ex:
            m = m * (1 - poly_mask(ex, feather=feather))
        return np.clip(m, 0, 1)

    def gate(self, m, lmin=None, lmax=None, soft=0.04):
        Y = lum(self.lin) ** (1 / 2.2)
        g = np.ones_like(Y)
        if lmin is not None:
            g *= np.clip((Y - lmin) / soft + 0.5, 0, 1)
        if lmax is not None:
            g *= np.clip((lmax - Y) / soft + 0.5, 0, 1)
        g = cv2.GaussianBlur(g, (0, 0), 1.0)
        return m * g

    # ------------------------------------------------------------ shading / paint
    def shading(self, mask, ref=None, **kw):
        sh, r = shading_map(self.base, mask, ref=ref, **kw)
        return sh, r

    def ref_of(self, mask, **kw):
        _, r = shading_map(self.base, mask, **kw)
        return r

    def paint(self, mask, color, shade):
        c = hex2rgb(color) if isinstance(color, str) else np.asarray(color, np.float32)
        new = lin2srgb(srgb2lin(c)[None, None, :] * shade[..., None])
        self.img = self.img * (1 - mask[..., None]) + new * mask[..., None]

    def texture(self, tex, origin, u, v, metres, mask=None, shade=None, opacity=1.0, shade_mix=1.0):
        self.img = decal(self.img, tex, self.cam, origin, u, v, metres, shade=shade, opacity=opacity, clip_mask=mask,
                         shade_mix=shade_mix)

    def quad_texture(self, tex_path, quad_src, mask=None, shade=None, opacity=1.0):
        """Warp a texture onto an image-space quad given in SOURCE px (TL, TR, BR, BL)."""
        from stagelib import warp_rgba
        tex = cv2.imread(tex_path, cv2.IMREAD_UNCHANGED)
        if tex.shape[2] == 3:
            tex = np.dstack([tex, np.full(tex.shape[:2], 255, np.uint8)])
        tex = cv2.cvtColor(tex, cv2.COLOR_BGRA2RGBA)
        h, w = tex.shape[:2]
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(np.asarray(quad_src) * S))
        col, a = warp_rgba(tex, Hm)
        a = a * opacity
        if mask is not None:
            a = a * mask
        if shade is not None:
            col = lin2srgb(srgb2lin(col) * shade[..., None])
        self.img = self.img * (1 - a[..., None]) + col * a[..., None]

    # ------------------------------------------------------------ 3D
    def layer3d(self, objects, room, light=None, tag="3d", catchers=True, render=True, occ=None):
        p = make_job(self.name, self.cam.scaled(1 / S), room, objects, light, tag=tag, catchers=catchers)
        if render:
            render_jobs([p])
        lay = load_rgba(f"{BASE}/out/{self.name}_{tag}.png")
        if occ is not None and not np.isscalar(occ):
            lay[..., 3] *= (1 - occ)
        self.img = over(self.img, lay)
        return lay

    # ------------------------------------------------------------ output
    def finish(self, tag, **grade_kw):
        out = grade(self.img, **grade_kw) if grade_kw else self.img
        cv2.imwrite(f"{OUT}/{tag}_after.jpg", to_bgr8(out), [cv2.IMWRITE_JPEG_QUALITY, 93])
        cv2.imwrite(f"{OUT}/{tag}_before.jpg", to_bgr8(self.before), [cv2.IMWRITE_JPEG_QUALITY, 93])
        return out


def hue_gate(stage, m, hmin, hmax, smin=0.25, vmin=0.1):
    hsv = cv2.cvtColor((np.clip(stage.base, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h = hsv[..., 0] * 2
    s = hsv[..., 1] / 255
    v = hsv[..., 2] / 255
    g = ((h >= hmin) & (h <= hmax) & (s >= smin) & (v >= vmin)).astype(np.float32)
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    return m * g
