import sys, json
sys.path.insert(0, "ep3")
import numpy as np, soundfile as sf
from plan import shots, GUSTS, SALUTE, DUR, chapters

voice, sr = sf.read("ep3/voice.wav")
n = int(DUR * sr)
t = np.arange(n) / sr
rng = np.random.default_rng(3)

# mood per shot: (base freq set, gain)
MOOD = {"sinking": 1.35, "navy": 1.3, "harbour_sail": 1.05, "underwater": 0.7, "test": 1.1}
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

for (gt, st) in GUSTS:
    add(gt - 0.4, whoosh(0.35 + st / 80, 2.4))
for st in SALUTE:
    for j in range(8):
        add(st + 1.0 + j * 0.18, boom(0.22, 1.6))
for s in shots:
    if s["shot"] == "navy":
        a_, b_ = int(s["start"] * sr), min(n, int(s["end"] * sr))
        mix[a_:b_] += np.convolve(rng.standard_normal(b_ - a_), np.ones(6) / 6, mode="same") * 0.06
    if s["shot"] == "sinking":
        a_, b_ = int(s["start"] * sr), min(n, int(s["end"] * sr))
        mix[a_:b_] += np.convolve(rng.standard_normal(b_ - a_), np.ones(40) / 40, mode="same") * 0.12
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
sf.write("ep3/mix.wav", out, sr)

# subtitles
REPL = [("eighteen forty-four", "1844"), ("eighteen nineties", "1890s"), ("nineteen twenty,", "1920,"), ("sixteen twenty-eight", "1628"), ("sixteen twenty-seven", "1627"), ("sixteen twenty-six", "1626"), ("sixteen twenty-five", "1625"),
        ("sixteen twenty-one", "1621"), ("sixteen sixties", "1660s"), ("sixteen hundreds", "1600s"), ("nineteen fifty-six", "1956"),
        ("nineteen fifty-nine", "1959"), ("nineteen sixty-one", "1961"), ("nineteen fifties", "1950s"), ("nineteen ninety", "1990"),
        ("three hundred and thirty-three", "333"), ("thirteen hundred", "1,300"), ("a hundred and twenty", "120"), ("thirty-two", "32"),
        ("seventy-two", "72"), ("twenty-four-pound", "24-pound"), ("forty-three", "43"), ("forty-five million", "45 million"),
        ("twelve hundred", "1,200"), ("one hundred and forty-five", "145"), ("three hundred", "300"), ("sixty-nine", "69"),
        ("five hundred", "500"), ("seventeen years", "17 years"), ("tenth of August", "10th of August"), ("sixteenth of January", "16th of January"),
        ("twenty-fourth of April", "24th of April")]
tim = json.load(open("ep3/timing.json"))
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
lines, k = [], 1
for p in tim:
    for s in p["sents"]:
        txt = s["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a.capitalize(), b)
        lines.append(f"{k}\n{ts(s['start'])} --> {ts(s['end'] + 0.2)}\n{txt}\n"); k += 1
open("out/Blunderbuss_Vasa.srt", "w").write("\n".join(lines))
# chapters for the YouTube description
ch = ["0:00 Intro"] + [f"{int(a//60)}:{int(a%60):02d} {title}" for (a, ps, nn, title) in chapters]
open("ep3/chapters.txt", "w").write("\n".join(ch))
print("\n".join(ch)); print("dur", round(DUR, 1))
