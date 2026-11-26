import json, random, sys
sys.path.insert(0, "ep5")
timing = json.load(open("ep5/timing.json"))
DUR = timing[-1]["end"] + 1.5
CHAP_GAP = 2.2
TAGS = {
 "arrival": "MARS · 23 SEPTEMBER 1999", "control": "JET PROPULSION LABORATORY, CALIFORNIA", "mars": "MARS", "orbiter": "MARS CLIMATE ORBITER · 638 KG",
 "launch": "CAPE CANAVERAL · 11 DECEMBER 1998", "cruise": "669 MILLION KM TO MARS", "units": "THE UNITS ERROR", "trajectory": "ARRIVAL ALTITUDE",
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

