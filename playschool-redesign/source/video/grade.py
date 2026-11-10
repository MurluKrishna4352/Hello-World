import subprocess, numpy as np, sys
IN = sys.argv[1]; OUT = sys.argv[2]
W, H = 360, 480
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", IN, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
n = len(fr); t = np.arange(n) / 30.0
p = np.array([np.percentile(f, 98) for f in fr]) / 255.0
k = 15; ps = np.convolve(np.pad(p, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
w = np.clip((t - 16.0) / 0.6, 0, 1)
out = np.empty_like(fr)
for i in range(n):
    a = fr[i].astype(np.float32) / 255
    if w[i] > 0:
        b = np.clip(a / max(ps[i], 0.05) * 0.95, 0, 1) ** 0.62
        a = a * (1 - w[i]) + b * w[i]
    out[i] = (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", IN, "-map", "0:v", "-map", "1:a", "-vf", "hqdn3d=3:2:4:4", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-g", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", OUT], stdin=subprocess.PIPE)
enc.stdin.write(out.tobytes()); enc.stdin.close(); enc.wait()
print("frames", n, "dur", n / 30)
