import sys, json
sys.path.insert(0, "ep4")
import numpy as np, soundfile as sf
from plan import shots, DUR, chapters, sent_time

voice, sr = sf.read("ep4/voice.wav")
n = int(DUR * sr)
t = np.arange(n) / sr
rng = np.random.default_rng(3)

# mood per shot: (base freq set, gain)
MOOD = {"collision": 1.35, "sinking": 1.4, "diagram_b": 1.25, "signals": 1.15, "ghost": 0.8, "wreck": 0.7}
gain = np.ones(n) * 0.85
for s in shots:
    a, b = int(s["start"] * sr), min(n, int(s["end"] * sr))
    gain[a:b] = MOOD.get(s["shot"], 0.85)
gain = np.convolve(gain, np.ones(sr) / sr, mode="same")  # smooth transitions

pad = np.zeros(n)
for f, g in [(73.4, 1), (110, 0.55), (146.8, 0.3), (220, 0.12), (87.3, 0.4)]:
    pad += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * g * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.03, 0.08) * t) ** 2)
wind = np.convolve(rng.standard_normal(n), np.ones(500) / 500, mode="same") * 4
bed = (pad * 0.045 + wind * 0.035) * gain

mix = bed.copy()
def add(at, sig):
    i = int(at * sr)
    if i >= n or i < 0: return
    m = min(len(sig), n - i); mix[i:i + m] += sig[:m]
def boom(g, length=1.4):
    m = int(length * sr); tt = np.arange(m) / sr
    nl = np.convolve(rng.standard_normal(m), np.ones(60) / 60, mode="same")
    return (nl * 2.2 + np.sin(2 * np.pi * (55 - 25 * tt) * tt) * 0.9) * np.exp(-tt * 4.5) * g
def whoosh(g=0.25, length=0.9):
    m = int(length * sr); tt = np.arange(m) / sr
    return np.convolve(rng.standard_normal(m), np.ones(25) / 25, mode="same") * np.sin(np.pi * tt / length) ** 2 * g * 3
def splash(g):
    m = int(0.9 * sr); tt = np.arange(m) / sr
    return np.convolve(rng.standard_normal(m), np.ones(8) / 8, mode="same") * np.exp(-tt * 5) * g

for s in shots:
    if s["shot"] == "collision":
        hit = sent_time(s, "It struck") or (s["start"] + 3.5)
        if s["idx"] == 1: hit = s["start"] + 3.2
        add(hit, boom(0.6, 2.5)); add(hit + 0.1, boom(0.4, 2.0))
    if s["shot"] == "sinking":
        a_, b_ = int(s["start"] * sr), min(n, int(s["end"] * sr))
        mix[a_:b_] += np.convolve(rng.standard_normal(b_ - a_), np.ones(40) / 40, mode="same") * 0.12
    if s["shot"] == "diagram_b":
        add(s["start"] + 7.5, boom(0.4, 2.0))
for s in shots[1:]:
    add(s["start"] - 0.5, whoosh(0.12))
for (a, ps, nn, title) in chapters:
    add(a + 0.1, boom(0.25, 2.0))
add(0.6, boom(0.35, 2.0))

v = np.zeros(n); v[:min(n, len(voice))] = voice[:n]
env = np.convolve(np.abs(v), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.4 * np.clip(env / (env.max() * 0.25), 0, 1)
out = v + mix * duck
fade = np.clip((DUR - t) / 1.5, 0, 1); out *= fade
out = out / np.abs(out).max() * 0.95
sf.write("ep4/mix.wav", out, sr)

# subtitles
REPL = [("eighteen ninety-three", "1893"), ("eighteen ninety-two", "1892"), ("eighteen nineties", "1890s"), ("eighteen sixty-six", "1866"),
        ("nineteen sixteen", "1916"), ("two thousand and four", "2004"), ("three hundred and fifty-eight", "358"),
        ("sixteen-and-a-quarter-inch", "16.25-inch"), ("twelve hundred", "1,200"), ("eight hundred", "800"), ("sixteen hundred", "1,600"),
        ("a hundred and forty", "140"), ("thirty metres", "30 metres"), ("twenty-second of June", "22nd of June"),
        ("twenty-second of August", "22nd of August"), ("three thirty", "3:30"), ("sixteen points", "16 points")]
tim = json.load(open("ep4/timing.json"))
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
lines, k = [], 1
for p in tim:
    for s in p["sents"]:
        txt = s["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a.capitalize(), b)
        lines.append(f"{k}\n{ts(s['start'])} --> {ts(s['end'] + 0.2)}\n{txt}\n"); k += 1
open("out/Blunderbuss_HMSVictoria.srt", "w").write("\n".join(lines))
# chapters for the YouTube description
ch = ["0:00 Intro"] + [f"{int(a//60)}:{int(a%60):02d} {title}" for (a, ps, nn, title) in chapters]
open("ep4/chapters.txt", "w").write("\n".join(ch))
print("\n".join(ch)); print("dur", round(DUR, 1))
