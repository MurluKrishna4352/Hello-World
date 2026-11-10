"""Joint camera fit: focal length + pose + free scene dimensions, from points and line observations.

Scene config (scenes/<name>.json) "calib" block:
  "f": [init, lo, hi]
  "vars": {"W": [init, lo, hi], ...}        free dimensions (metres)
  "fixed": {"H": 3.0}
  "points": [{"world": ["0","0","0"], "img": [x, y]}]     world entries may be expressions of vars
  "lines":  [{"p0": [...], "dir": [...], "img": [[x,y],...], "w": 1.0}]
  "cxcy": [cx, cy] optional principal point
Writes out/<name>_cam.json (+ resolved dims) and out/<name>_overlay.png.
"""
from __future__ import annotations

import json
import os
import sys

import cv2
import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cam import Camera, overlay  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))


def ev(expr, env):
    if isinstance(expr, (int, float)):
        return float(expr)
    return float(eval(str(expr), {"__builtins__": {}}, env))


def load_frame(cfg):
    img = cv2.imread(cfg["frame"])
    if cfg.get("bright"):
        a = img.astype(np.float32) / 255
        p = np.percentile(a, 98)
        a = np.clip(a / p * 0.95, 0, 1) ** 0.6
        img = (a * 255).astype(np.uint8)
    return img


def fit(cfg):
    c = cfg["calib"]
    img = load_frame(cfg)
    size = (img.shape[1], img.shape[0])
    cx, cy = c.get("cxcy", [size[0] / 2, size[1] / 2])
    vnames = list(c.get("vars", {}).keys())
    fixed = dict(c.get("fixed", {}))
    f0, flo, fhi = c["f"]

    def env_of(vv):
        e = dict(fixed)
        e.update({k: v for k, v in zip(vnames, vv)})
        return e

    def residuals(p, return_cam=False):
        f = p[0]
        rvec = p[1:4]
        tvec = p[4:7]
        vv = p[7:]
        env = env_of(vv)
        K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]])
        cam = Camera(K, rvec, tvec, size)
        if return_cam:
            return cam, env
        res = []
        for pt in c["points"]:
            w = [ev(x, env) for x in pt["world"]]
            q = cam.project([w])[0]
            wt = pt.get("w", 1.0)
            res += list((q - np.asarray(pt["img"])) * wt)
            if cam.depth([w])[0] <= 0.05:
                res += [1e3]
            else:
                res += [0]
        for ln in c.get("lines", []):
            p0 = np.array([ev(x, env) for x in ln["p0"]])
            d = np.array([ev(x, env) for x in ln["dir"]])
            a, b = cam.project([p0, p0 + d * 0.3])
            n = np.array([-(b - a)[1], (b - a)[0]])
            n /= np.linalg.norm(n) + 1e-9
            wt = ln.get("w", 1.0)
            for q in ln["img"]:
                res.append(float(np.dot(np.asarray(q) - a, n)) * wt)
        return np.array(res)

    # initial pose from solvePnP on the points using init values
    env0 = env_of([c["vars"][k][0] for k in vnames])
    wp = np.array([[ev(x, env0) for x in pt["world"]] for pt in c["points"]], float)
    ip = np.array([pt["img"] for pt in c["points"]], float)
    best = None
    init = c.get("init")
    for fi in np.linspace(flo, fhi, 12):
        K = np.array([[fi, 0, cx], [0, fi, cy], [0, 0, 1]])
        if init:
            C0 = np.array(init["cam"], float); T0 = np.array(init["look"], float)
            fwd = T0 - C0; fwd /= np.linalg.norm(fwd)
            right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
            down = np.cross(fwd, right)
            Rm = np.stack([right, down, fwd])
            rv, _ = cv2.Rodrigues(Rm); tv = (-Rm @ C0).reshape(3, 1)
        else:
            planar = np.linalg.matrix_rank(wp - wp.mean(0), tol=1e-6) < 3
            ok, rv, tv = cv2.solvePnP(wp, ip, K, None, flags=cv2.SOLVEPNP_IPPE if planar else cv2.SOLVEPNP_ITERATIVE)
            if not ok:
                continue
        p = np.concatenate([[fi], rv.ravel(), tv.ravel(), [c["vars"][k][0] for k in vnames]])
        lo = [flo] + [-np.inf] * 6 + [c["vars"][k][1] for k in vnames]
        hi = [fhi] + [np.inf] * 6 + [c["vars"][k][2] for k in vnames]
        p = np.clip(p, np.array(lo) + 1e-6, np.array(hi) - 1e-6)
        r = least_squares(residuals, p, bounds=(lo, hi), loss="soft_l1", f_scale=3.0)
        cost = float(np.sum(residuals(r.x) ** 2))
        if best is None or cost < best[0]:
            best = (cost, r.x)
    cam, env = residuals(best[1], return_cam=True)
    n_obs = len(residuals(best[1]))
    return cam, env, best[0], n_obs, img


def main(name):
    cfg = json.load(open(f"{BASE}/scenes/{name}.json"))
    cam, env, cost, n, img = fit(cfg)
    print(f"{name}: f={cam.K[0,0]:.1f} rms={np.sqrt(cost/max(n,1)):.2f}px vars={ {k: round(v,3) for k,v in env.items()} } "
          f"cam_centre={np.round(cam.center(),2)}")
    out = cam.to_json()
    out["dims"] = env
    json.dump(out, open(f"{BASE}/out/{name}_cam.json", "w"), indent=1)
    room = {k: (ev(v, env) if not isinstance(v, (int, float)) else v) for k, v in cfg["room"].items()}
    s = 2
    big = cv2.resize(img, (img.shape[1] * s, img.shape[0] * s), interpolation=cv2.INTER_LANCZOS4)
    ov = overlay(big, cam.scaled(s), room)
    for pt in cfg["calib"]["points"]:
        cv2.circle(ov, tuple((np.array(pt["img"]) * s).astype(int)), 5, (0, 0, 255), 2)
    for ln in cfg["calib"].get("lines", []):
        for q in ln["img"]:
            cv2.drawMarker(ov, tuple((np.array(q) * s).astype(int)), (0, 255, 0), cv2.MARKER_CROSS, 12, 2)
    cv2.imwrite(f"{BASE}/out/{name}_overlay.png", ov)


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        main(nm)
