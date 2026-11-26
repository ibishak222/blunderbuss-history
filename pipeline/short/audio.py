import json, numpy as np, soundfile as sf, sys
sys.argv = ["x", "0", "1"]
voice, sr = sf.read("voice.wav")
timing = json.load(open("timing.json"))
T = [x["start"] for x in timing]
dur = timing[-1]["end"] + 0.9
n = int(dur * sr)
t = np.arange(n) / sr
rng = np.random.default_rng(1)

def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

# dark drone bed: D minor-ish low pad with slow swell
pad = sum(np.sin(2 * np.pi * f * t + p) * g for f, p, g in [(73.4, 0, 1), (110, 1, 0.6), (146.8, 2, 0.35), (174.6, 3, 0.25)])
pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t) ** 2
wind = np.convolve(rng.standard_normal(n), np.ones(400) / 400, mode="same") * 3
bed = (pad * 0.05 + wind * 0.03)
bed *= np.clip(t / 1.5, 0, 1) * np.clip((dur - t) / 1.5, 0, 1)
# lift tension during the attack, darker after
bed *= np.where((t > T[4]) & (t < T[7]), 1.5, 1.0)

mix = bed.copy()
def boom(at, gain=0.5, length=1.4):
    i = int(at * sr); m = int(length * sr)
    if i >= n: return
    m = min(m, n - i); tt = np.arange(m) / sr
    noise = rng.standard_normal(m)
    nl = np.convolve(noise, np.ones(60) / 60, mode="same")
    thump = np.sin(2 * np.pi * (55 - 25 * tt) * tt)
    env = np.exp(-tt * 4.5)
    mix[i:i + m] += (nl * 2.2 + thump * 0.9) * env * gain

def whoosh(at, gain=0.25, length=0.6):
    i = int((at - length * 0.7) * sr); m = int(length * sr)
    if i < 0: return
    tt = np.arange(m) / sr
    noise = np.convolve(rng.standard_normal(m), np.ones(25) / 25, mode="same")
    env = np.sin(np.pi * tt / length) ** 2
    mix[i:i + m] += noise * env * gain * 3

# gunfire matches the render's muzzle-flash schedule
import random
random.seed(2)
FIRE = T[4] + 1.0
for s in sorted(FIRE + random.uniform(0, 7.5) for _ in range(16)):
    boom(s, gain=random.uniform(0.12, 0.3))
cuts = [T[3] - 0.15, T[7] - 0.15, T[8] - 0.12, T[9] - 0.12]
for c in cuts: whoosh(c)
boom(T[0] + 0.05, 0.35)  # opening hit
boom(cuts[3], 0.3)

# duck the bed under the voice
v = np.zeros(n); v[:len(voice)] = voice[:n]
envv = np.convolve(np.abs(v), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.45 * np.clip(envv / (envv.max() * 0.25), 0, 1)
out = v * 1.0 + mix * duck
out = out / np.abs(out).max() * 0.95
sf.write("video/mix.wav", out, sr)
print("mix", round(dur, 2))
