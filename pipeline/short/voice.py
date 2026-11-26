import json, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
lines = [
    "In nineteen-oh-four, the Russian Navy went to war... with a fleet of British fishermen.",
    "Russia was fighting Japan, so it sent its Baltic Fleet halfway around the world.",
    "The crews were terrified of Japanese torpedo boats. And they saw them everywhere.",
    "Just before one in the morning, on the Dogger Bank in the North Sea, they spotted small boats.",
    "Searchlights on. Guns firing.",
    "But these weren't torpedo boats. They were fishing trawlers from Hull, nets down, unable to run.",
    "The trawler Crane sank, and two fishermen were killed. In the chaos, Russian ships even hit one of their own.",
    "Britain and Russia came close to war. Russia paid sixty-six thousand pounds.",
    "And the fleet? It sailed on to Japan... and was destroyed at Tsushima.",
    "Follow for more of history's biggest blunders.",
]
k = Kokoro("tts/kokoro.onnx", "tts/voices.bin")
sr = 24000
out, timing, t = [], [], 0.35
out.append(np.zeros(int(0.35 * sr), dtype=np.float32))
for ln in lines:
    a, sr = k.create(ln, voice=VOICE, speed=1.08, lang="en-us")
    # trim leading/trailing near-silence
    idx = np.where(np.abs(a) > 0.01)[0]
    if len(idx):
        a = a[max(0, idx[0] - 600): idx[-1] + 1200]
    d = len(a) / sr
    timing.append({"text": ln, "start": round(t, 3), "end": round(t + d, 3)})
    out.append(a.astype(np.float32))
    gap = 0.28
    out.append(np.zeros(int(gap * sr), dtype=np.float32))
    t += d + gap
audio = np.concatenate(out)
sf.write("voice.wav", audio, sr)
json.dump(timing, open("timing.json", "w"), indent=1)
print(VOICE, "total", round(len(audio) / sr, 2))
for x in timing:
    print(x["start"], x["end"], x["text"][:50])
