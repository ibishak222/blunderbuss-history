import json, sys, re
sys.path.insert(0, "long")
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script import SCRIPT

k = Kokoro("tts/kokoro.onnx", "tts/voices.bin")
SR = 24000
def sentences(p):
    return [s.strip() for s in re.split(r'(?<=[.?!])\s+', p) if s.strip()]

out, timing, t = [np.zeros(int(0.6 * SR), np.float32)], [], 0.6
for i, (shot, chapter, para) in enumerate(SCRIPT):
    if chapter:  # breathing room for the chapter card
        pad = 2.2
        out.append(np.zeros(int(pad * SR), np.float32)); t += pad
    p0 = t
    sents = []
    for s in sentences(para):
        a, _ = k.create(s, voice="af_heart", speed=1.0, lang="en-us")
        idx = np.where(np.abs(a) > 0.01)[0]
        if len(idx): a = a[max(0, idx[0] - 600): idx[-1] + 1200]
        d = len(a) / SR
        sents.append({"text": s, "start": round(t, 3), "end": round(t + d, 3)})
        out.append(a.astype(np.float32)); t += d
        gap = 0.32
        out.append(np.zeros(int(gap * SR), np.float32)); t += gap
    out.append(np.zeros(int(0.35 * SR), np.float32)); t += 0.35
    timing.append({"i": i, "shot": shot, "chapter": chapter, "start": round(p0, 3), "end": round(t, 3), "sents": sents})
    print(i, shot, round(p0, 1), round(t, 1), flush=True)
out.append(np.zeros(int(1.5 * SR), np.float32)); t += 1.5
sf.write("long/voice.wav", np.concatenate(out), SR)
json.dump(timing, open("long/timing.json", "w"), indent=1)
print("TOTAL", round(t, 1))
