import json, random, sys
sys.path.insert(0, "ep4")
timing = json.load(open("ep4/timing.json"))
DUR = timing[-1]["end"] + 1.5
CHAP_GAP = 2.2
TAGS = {
 "fleet": "OFF TRIPOLI · 22 JUNE 1893", "victoria": "HMS VICTORIA · 'THE SLIPPER'", "tryon": "VICE-ADMIRAL SIR GEORGE TRYON", "bridge": "THE BRIDGE OF HMS VICTORIA",
 "signals": "THE SIGNAL: TURN 16 POINTS INWARDS", "diagram_a": "SIX CABLES = 1,200 YARDS", "diagram_b": "3:30 PM", "collision": "HMS CAMPERDOWN RAMS HMS VICTORIA",
 "sinking": "ABOUT FIFTEEN MINUTES", "rescue": "THE SURVIVORS", "ghost": "LONDON · THE SAME AFTERNOON (LEGEND)", "jellicoe": "JUTLAND · 1916", "wreck": "140 METRES DOWN · FOUND 2004",
}
shots = []
for p in timing:
    start = p["start"] - (CHAP_GAP if p["chapter"] else 0)
    if shots and shots[-1]["shot"] == p["shot"] and not p["chapter"]:
        shots[-1]["paras"].append(p)
    else:
        shots.append({"shot": p["shot"], "start": start, "paras": [p], "chapter": p["chapter"], "para_start": p["start"]})
for i, s in enumerate(shots):
    s["end"] = shots[i + 1]["start"] if i + 1 < len(shots) else DUR
    s["idx"] = i
    s["sents"] = [x for p in s["paras"] for x in p["sents"]]
chapters, n = [], 0
for s in shots:
    if s["chapter"]:
        n += 1; chapters.append((s["start"], s["para_start"], n, s["chapter"]))

def sent_time(shot, needle):
    for x in shot["sents"]:
        if needle.lower() in x["text"].lower():
            return x["start"]
    return None

