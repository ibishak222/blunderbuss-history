import sys, json
sys.path.insert(0, "ep5")
import numpy as np, soundfile as sf
from plan import shots, DUR, chapters, sent_time

voice, sr = sf.read("ep5/voice.wav")
n = int(DUR * sr)
t = np.arange(n) / sr
rng = np.random.default_rng(3)

# mood per shot: (base freq set, gain)
MOOD = {"arrival": 1.3, "trajectory": 1.2, "launch": 1.2, "control": 1.0, "units": 1.0}
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
    if s["shot"] == "launch":
        lt0 = sent_time(s, "launched") or s["start"] + 2
        m = int(8 * sr); tt = np.arange(m) / sr
        rum = np.convolve(rng.standard_normal(m), np.ones(200) / 200, mode="same") * 6 * np.clip(tt / 0.6, 0, 1) * np.exp(-tt / 5)
        add(lt0 + 0.6, rum)
    if s["shot"] == "arrival":
        bt = sent_time(s, "insertion burn") or sent_time(s, "fired its engine")
        if bt:
            m = int(6 * sr); tt = np.arange(m) / sr
            add(bt, np.convolve(rng.standard_normal(m), np.ones(120) / 120, mode="same") * 2.5 * np.clip(tt / 0.5, 0, 1) * np.clip((6 - tt) / 1, 0, 1))
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
sf.write("ep5/mix.wav", out, sr)

# subtitles
REPL = [("nineteen ninety-nine", "1999"), ("nineteen ninety-eight", "1998"), ("nineteen ninety-seven", "1997"), ("nineteen ninety-three", "1993"),
        ("nineteen nineties", "1990s"), ("six hundred and sixty-nine million", "669 million"), ("six hundred and thirty-eight", "638"),
        ("three hundred and twenty-seven million dollars", "$327 million"), ("three hundred million dollar", "$300 million"),
        ("four point four five", "4.45"), ("two hundred and twenty-six", "226"), ("One hundred and seventy", "170"), ("One hundred and fifty", "150"),
        ("a hundred and ten", "110"), ("fifty-seven", "57"), ("thirty percent", "30%"), ("Twenty-four hours", "24 hours"), ("forty-nine", "49"),
        ("eighty.", "80."), ("ninety-eight", "'98"), ("twenty-third of September", "23rd of September"), ("eleventh of December", "11th of December"),
        ("Delta Two", "Delta II")]
tim = json.load(open("ep5/timing.json"))
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
lines, k = [], 1
for p in tim:
    for s in p["sents"]:
        txt = s["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a.capitalize(), b)
        lines.append(f"{k}\n{ts(s['start'])} --> {ts(s['end'] + 0.2)}\n{txt}\n"); k += 1
open("out/Blunderbuss_MarsClimateOrbiter.srt", "w").write("\n".join(lines))
# chapters for the YouTube description
ch = ["0:00 Intro"] + [f"{int(a//60)}:{int(a%60):02d} {title}" for (a, ps, nn, title) in chapters]
open("ep5/chapters.txt", "w").write("\n".join(ch))
print("\n".join(ch)); print("dur", round(DUR, 1))
