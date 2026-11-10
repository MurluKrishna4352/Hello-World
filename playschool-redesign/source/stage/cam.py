"""Camera calibration + projection helpers for virtual staging of real video frames.

World convention (per scene): x to the right along the main wall, y up, z towards the camera.
Units: metres. Image coordinates are given in SOURCE pixels (360x480 frames) and scaled by `scale`.
"""
from __future__ import annotations

import json
import math
import sys

import cv2
import numpy as np


class Camera:
    def __init__(self, K, rvec, tvec, size):
        self.K = np.asarray(K, dtype=np.float64)
        self.rvec = np.asarray(rvec, dtype=np.float64).reshape(3, 1)
        self.tvec = np.asarray(tvec, dtype=np.float64).reshape(3, 1)
        self.size = tuple(size)  # (w, h)
        self.R, _ = cv2.Rodrigues(self.rvec)

    def scaled(self, s):
        K = self.K.copy()
        K[0, :] *= s
        K[1, :] *= s
        return Camera(K, self.rvec, self.tvec, (int(round(self.size[0] * s)), int(round(self.size[1] * s))))

    def project(self, pts):
        pts = np.asarray(pts, dtype=np.float64).reshape(-1, 3)
        img, _ = cv2.projectPoints(pts, self.rvec, self.tvec, self.K, None)
        return img.reshape(-1, 2)

    def depth(self, pts):
        pts = np.asarray(pts, dtype=np.float64).reshape(-1, 3)
        return (self.R @ pts.T + self.tvec)[2]

    def center(self):
        return (-self.R.T @ self.tvec).ravel()

    def plane_homography(self, origin, u_axis, v_axis, tex_size, metres):
        """Homography mapping texture pixels (tw x th covering `metres`=(mu,mv) along u,v) to image px."""
        o = np.asarray(origin, float)
        u = np.asarray(u_axis, float)
        v = np.asarray(v_axis, float)
        tw, th = tex_size
        mu, mv = metres
        corners_w = [o, o + u * mu, o + u * mu + v * mv, o + v * mv]
        corners_t = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]])
        corners_i = np.float32(self.project(corners_w))
        return cv2.getPerspectiveTransform(corners_t, corners_i)

    def to_json(self):
        return {"K": self.K.tolist(), "rvec": self.rvec.ravel().tolist(), "tvec": self.tvec.ravel().tolist(),
                "size": list(self.size)}

    @staticmethod
    def from_json(d):
        return Camera(d["K"], d["rvec"], d["tvec"], d["size"])

    def threejs(self, near=0.05, far=60.0):
        """Return projection + view matrices (column-major lists) for three.js."""
        w, h = self.size
        fx, fy, cx, cy = self.K[0, 0], self.K[1, 1], self.K[0, 2], self.K[1, 2]
        P = np.array([
            [2 * fx / w, 0, 1 - 2 * cx / w, 0],
            [0, 2 * fy / h, 2 * cy / h - 1, 0],
            [0, 0, -(far + near) / (far - near), -2 * far * near / (far - near)],
            [0, 0, -1, 0]])
        V = np.eye(4)
        V[:3, :3] = self.R
        V[:3, 3] = self.tvec.ravel()
        F = np.diag([1, -1, -1, 1])
        V = F @ V
        return {"projection": P.T.ravel().tolist(), "view": V.T.ravel().tolist(),
                "viewInverse": np.linalg.inv(V).T.ravel().tolist()}


def solve(img_pts, world_pts, size, f=None, f_range=(120, 900), lines=(), cx=None, cy=None):
    """Solve pose (and optionally focal length) from point correspondences.

    lines: [{"p0": [x,y,z], "dir": [dx,dy,dz], "img": [[x,y],...]}] extra constraints: observed image points must
    lie on the projection of the world line.
    """
    img = np.asarray(img_pts, dtype=np.float64).reshape(-1, 2)
    wp = np.asarray(world_pts, dtype=np.float64).reshape(-1, 3)
    w, h = size
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    planar = np.linalg.matrix_rank(wp - wp.mean(0), tol=1e-6) < 3

    def attempt(fv):
        K = np.array([[fv, 0, cx], [0, fv, cy], [0, 0, 1]], float)
        flag = cv2.SOLVEPNP_IPPE if planar and len(wp) >= 4 else cv2.SOLVEPNP_ITERATIVE
        ok, rvec, tvec = cv2.solvePnP(wp, img, K, None, flags=flag)
        if not ok:
            return None
        rvec, tvec = cv2.solvePnPRefineLM(wp, img, K, None, rvec, tvec)
        cam = Camera(K, rvec, tvec, size)
        err = np.sum((cam.project(wp) - img) ** 2)
        for ln in lines:
            p0 = np.asarray(ln["p0"], float)
            d = np.asarray(ln["dir"], float)
            a, b = cam.project([p0, p0 + d * 0.5])
            n = np.array([-(b - a)[1], (b - a)[0]])
            n /= np.linalg.norm(n) + 1e-9
            for q in ln["img"]:
                err += float(np.dot(np.asarray(q) - a, n)) ** 2
        if np.any(cam.depth(wp) <= 0):
            err += 1e9
        return err, cam

    if f is not None:
        return attempt(f)[1], attempt(f)[0]
    best = None
    for fv in np.geomspace(f_range[0], f_range[1], 160):
        r = attempt(fv)
        if r and (best is None or r[0] < best[0]):
            best = (r[0], fv, r[1])
    # refine
    lo, hi = best[1] * 0.95, best[1] * 1.05
    for fv in np.linspace(lo, hi, 60):
        r = attempt(fv)
        if r and r[0] < best[0]:
            best = (r[0], fv, r[1])
    return best[2], best[0]


def overlay(img, cam, room, grid=0.5, color=(0, 255, 255)):
    """Draw room wireframe + floor grid. room = dict(W=, H=, D=, z0=0)."""
    out = img.copy()
    W, H, D = room["W"], room["H"], room["D"]
    z0 = room.get("z0", 0.0)

    def seg(a, b, c=color, t=1):
        # clip segments behind camera by sampling
        pts = np.linspace(a, b, 40)
        dep = cam.depth(pts)
        pts = pts[dep > 0.05]
        if len(pts) < 2:
            return
        p = cam.project(pts).astype(np.int32)
        cv2.polylines(out, [p], False, c, t, cv2.LINE_AA)

    for x in np.arange(0, W + 1e-6, grid):
        seg([x, 0, z0], [x, 0, z0 + D], (0, 200, 255))
    for z in np.arange(z0, z0 + D + 1e-6, grid):
        seg([0, 0, z], [W, 0, z], (0, 200, 255))
    box = [([0, 0, z0], [W, 0, z0]), ([0, H, z0], [W, H, z0]), ([0, 0, z0], [0, H, z0]), ([W, 0, z0], [W, H, z0]),
           ([0, 0, z0], [0, 0, z0 + D]), ([W, 0, z0], [W, 0, z0 + D]), ([0, H, z0], [0, H, z0 + D]),
           ([W, H, z0], [W, H, z0 + D])]
    for a, b in box:
        seg(a, b, (255, 0, 255), 2)
    return out


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    print(cfg)


def backproject(cam, px, plane_point, plane_normal):
    """Image pixel(s) (in cam's pixel space) -> world point(s) on a plane."""
    px = np.atleast_2d(np.asarray(px, float))
    Kinv = np.linalg.inv(cam.K)
    C = cam.center()
    n = np.asarray(plane_normal, float)
    p0 = np.asarray(plane_point, float)
    out = []
    for u, v in px:
        d_cam = Kinv @ np.array([u, v, 1.0])
        d = cam.R.T @ d_cam
        t = np.dot(p0 - C, n) / np.dot(d, n)
        out.append(C + t * d)
    return np.array(out)
