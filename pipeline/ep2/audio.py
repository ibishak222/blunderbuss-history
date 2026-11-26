import sys, json
sys.path.insert(0, "ep2")
import numpy as np, soundfile as sf
from plan import shots, BURSTS, DUR, chapters

voice, sr = sf.read("ep2/voice.wav")
n = int(DUR * sr)
t = np.arange(n) / sr
rng = np.random.default_rng(3)

# mood per shot: (base freq set, gain)
MOOD = {"gunline": 1.3, "dam": 1.3, "truck": 1.3, "rain": 1.0, "trenches": 1.1}
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

def rattle(n=9, rate=0.075, g=0.16):
    out = np.zeros(int((n * rate + 0.6) * sr))
    for j in range(n):
        b_ = boom(g * rng.uniform(0.8, 1.1), 0.35)
        i = int(j * rate * sr); m = min(len(b_), len(out) - i); out[i:i + m] += b_[:m]
    return out
for (bt, idx) in BURSTS:
    add(bt, rattle(rng.integers(6, 11)))
# rain bed
for s in shots:
    if s["shot"] == "rain":
        a_, b_ = int(s["start"] * sr), min(n, int(s["end"] * sr))
        mix[a_:b_] += np.convolve(rng.standard_normal(b_ - a_), np.ones(6) / 6, mode="same") * 0.06
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
sf.write("ep2/mix.wav", out, sr)

# subtitles
REPL = [("nineteen thirty-two", "1932"), ("nineteen thirty-three", "1933"), ("nineteen thirty-four", "1934"), ("nineteen forty-three", "1943"),
        ("nineteen forty-eight", "1948"), ("nineteen fifty", "1950"), ("nineteen twenty-nine", "1929"), ("twenty twenty-three", "2023"),
        ("nine hundred and eighty-six", "986"), ("nine thousand eight hundred and sixty", "9,860"), ("two and a half thousand", "2,500"),
        ("fifty-seven thousand", "57,000"), ("twenty thousand", "20,000"), ("ten thousand", "10,000"), ("two hundred thousand", "200,000"),
        ("half a million", "500,000"), ("fifty kilometres an hour", "50 km/h"), ("three hundred", "300")]
tim = json.load(open("ep2/timing.json"))
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
lines, k = [], 1
for p in tim:
    for s in p["sents"]:
        txt = s["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a.capitalize(), b)
        lines.append(f"{k}\n{ts(s['start'])} --> {ts(s['end'] + 0.2)}\n{txt}\n"); k += 1
open("out/Blunderbuss_EmuWar.srt", "w").write("\n".join(lines))
# chapters for the YouTube description
ch = ["0:00 Intro"] + [f"{int(a//60)}:{int(a%60):02d} {title}" for (a, ps, nn, title) in chapters]
open("ep2/chapters.txt", "w").write("\n".join(ch))
print("\n".join(ch)); print("dur", round(DUR, 1))
