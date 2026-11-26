import json, random, sys
sys.path.insert(0, "ep2")
timing = json.load(open("ep2/timing.json"))
DUR = timing[-1]["end"] + 1.5
CHAP_GAP = 2.2
TAGS = {
 "gunline": "CAMPION, WESTERN AUSTRALIA · 1932", "emus_field": "THE WHEATBELT · WESTERN AUSTRALIA", "trenches": "THE FIRST WORLD WAR",
 "farm": "A SOLDIER SETTLER'S FARM", "emu_close": "DROMAIUS NOVAEHOLLANDIAE · THE EMU", "fence": "THE WHEATBELT", "gun_crew": "MAJOR MEREDITH'S UNIT",
 "rain": "OCTOBER 1932", "dam": "THE DAM AMBUSH · 4 NOVEMBER 1932", "lookout": "THE LOOKOUT", "truck": "THE TRUCK-MOUNTED GUN", "coat": "TODAY",
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

# fire windows per shot: list of (start, end) during which the gun bursts; and "scatter" time when emus run off
FIRE, SCATTER = {}, {}
for s in shots:
    k, a, b = s["shot"], s["start"], s["end"]
    if k == "gunline":
        if s["idx"] == 0:
            FIRE[s["idx"]] = [(a + 2.5, b)]; SCATTER[s["idx"]] = a + 5.5
        else:
            f0 = sent_time(s, "first burst") or sent_time(s, "killed in the first") or (a + 3)
            FIRE[s["idx"]] = [(f0, min(b, f0 + 9))]; SCATTER[s["idx"]] = f0 + 0.6
    if k == "dam":
        f0 = sent_time(s, "opened fire") or a + 10
        j = sent_time(s, "gun jammed") or f0 + 3
        FIRE[s["idx"]] = [(f0, j + 1.6)]; SCATTER[s["idx"]] = j + 2.2
    if k == "truck":
        FIRE[s["idx"]] = [(a + 2.5, b)]; SCATTER[s["idx"]] = a

BURSTS = []  # (t, shot_idx) individual bursts of ~0.8s
rng = random.Random(9)
for idx, wins in FIRE.items():
    for (a, b) in wins:
        t = a
        while t < b - 0.3:
            BURSTS.append((t, idx)); t += rng.uniform(1.0, 2.2)
BURSTS.sort()
