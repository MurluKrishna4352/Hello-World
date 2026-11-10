import json, sys, os
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from cam import solve, overlay, Camera
name = sys.argv[1]
base = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(f"{base}/scenes/{name}.json"))
img = cv2.imread(cfg["frame"])
if cfg.get("bright"):
    a = img.astype(np.float32)/255; p = np.percentile(a, 98); a = np.clip(a/p*0.95, 0, 1)**0.6; img = (a*255).astype(np.uint8)
size = (img.shape[1], img.shape[0])
c = cfg["calib"]
pts = c["points"]
cam, err = solve([p["img"] for p in pts], [p["world"] for p in pts], size, f=c.get("f"), lines=c.get("lines", []),
                 f_range=tuple(c.get("f_range", (120, 900))))
print(name, "f=%.1f err=%.2f" % (cam.K[0, 0], err), "cam centre", np.round(cam.center(), 2))
for p in pts:
    print("  ", p["world"], p["img"], np.round(cam.project([p["world"]])[0], 1))
json.dump(cam.to_json(), open(f"{base}/out/{name}_cam.json", "w"))
s = 2
big = cv2.resize(img, (size[0]*s, size[1]*s), interpolation=cv2.INTER_LANCZOS4)
ov = overlay(big, cam.scaled(s), cfg["room"])
for p in pts:
    q = (np.array(p["img"]) * s).astype(int)
    cv2.circle(ov, tuple(q), 5, (0, 0, 255), 2)
for ln in c.get("lines", []):
    for q in ln["img"]:
        cv2.drawMarker(ov, tuple((np.array(q)*s).astype(int)), (0, 255, 0), cv2.MARKER_CROSS, 12, 2)
cv2.imwrite(f"{base}/out/{name}_overlay.png", ov)
