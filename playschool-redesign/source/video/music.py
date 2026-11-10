"""Procedural, license-free light music bed (plucked arpeggios + bass + music box + shaker + pad)."""
import sys
import wave

import numpy as np

SR = 48000
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
OUT = sys.argv[1]
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)
N = int(DUR * SR) + SR * 3
L = np.zeros(N)
R = np.zeros(N)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4)


def pluck(f, dur=1.2, bright=0.5):
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    buf = np.convolve(buf, [bright, 1 - bright], mode="same")
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    env = np.minimum(1, np.arange(n) / (0.003 * SR))
    return out * env


def bell(f, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3.0) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9))
    return s * np.minimum(1, t / 0.002)


def bass(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.02) * np.exp(-t * 1.2)
    return s * env


def pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.004 * t) for f in freqs) / (2 * len(freqs))
    a = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    return s * a


def shaker(dur=0.08):
    n = int(dur * SR)
    s = rng.uniform(-1, 1, n)
    s = np.diff(np.concatenate([[0], s]))  # high-passed
    return s * np.exp(-np.arange(n) / (0.018 * SR))


# chord: (root midi, third, fifth)
CH = {"C": (48, 52, 55), "G": (43, 47, 50), "Am": (45, 48, 52), "F": (41, 45, 48), "Dm": (50, 53, 57), "Em": (52, 55, 59)}
PROG = ["C", "G", "Am", "F", "C", "F", "G", "C"]
MEL = [  # (beat offset within 2 bars, midi) — gentle pentatonic phrases
    [(0, 76), (1, 79), (2, 81), (3, 79), (4, 76), (6, 74)],
    [(0, 72), (1, 74), (2, 76), (4, 79), (5, 76), (6, 74)],
    [(0, 76), (2, 79), (3, 84), (4, 81), (6, 79)],
    [(0, 81), (1, 79), (2, 76), (3, 74), (4, 72), (6, 72)],
]
nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    ch = CH[PROG[b % len(PROG)]]
    last = b >= nbars - 1
    # arpeggio (8ths) one octave up
    pat = [0, 2, 1, 2, 0, 2, 1, 2]
    notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12]
    for k, idx in enumerate(pat):
        if last and k > 0:
            break
        add(pluck(midi(notes[idx] + (12 if (k == 3 and b % 2) else 0)), 1.4 if not last else 3.5, 0.45), t0 + k * BEAT / 2,
            pan=-0.35 + 0.1 * (k % 2), gain=0.32)
    # bass
    if b >= 1:
        add(bass(midi(ch[0] - 12), BAR * 0.95), t0, 0, 0.42)
        if not last:
            add(bass(midi(ch[2] - 12), BAR * 0.45), t0 + 2.5 * BEAT, 0, 0.22)
    # pad
    if b >= 2:
        add(pad([midi(n + 12) for n in ch], BAR + 0.3), t0, 0.0, 0.10)
    # music box melody every 2 bars, from bar 2
    if b >= 2 and b % 2 == 0 and not last:
        for off, m in MEL[(b // 2) % len(MEL)]:
            add(bell(midi(m)), t0 + off * BEAT, pan=0.35, gain=0.20)
    # shaker on off-beats from bar 4
    if b >= 4 and not last:
        for k in range(8):
            add(shaker(), t0 + k * BEAT / 2 + 0.02, pan=0.2, gain=0.05 if k % 2 else 0.025)

mix = np.stack([L, R], 1)[: int(DUR * SR)]
fade_out = int(3.0 * SR)
mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None] ** 1.5
mix[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.85
pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", OUT, DUR, "s")
