import json, random, sys
sys.path.insert(0, "ep3")
timing = json.load(open("ep3/timing.json"))
DUR = timing[-1]["end"] + 1.5
CHAP_GAP = 2.2
TAGS = {
 "harbour_sail": "STOCKHOLM · 10 AUGUST 1628", "sinking": "TEGELVIKEN, STOCKHOLM", "king": "GUSTAVUS ADOLPHUS · KING OF SWEDEN",
 "navy": "THE BAY OF RIGA · 1625", "shipyard": "THE NAVAL SHIPYARD, STOCKHOLM", "plans": "TWO FULL GUN DECKS", "carvings": "NEARLY 500 SCULPTURES",
 "test": "THE STABILITY TEST · SUMMER 1628", "underwater": "32 METRES DOWN", "raising": "STOCKHOLM HARBOUR · 1959–1961", "museum": "THE VASA MUSEUM · STOCKHOLM",
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

# key moments
GUSTS = []   # (time, strength)
for s in shots:
    for needle, strength in (("a gust of wind hit", 16), ("a gust of wind caught", 22), ("a stronger gust struck", 30)):
        t = sent_time(s, needle)
        if t: GUSTS.append((t + 0.4, strength))
SALUTE = [t for t in (sent_time(s, "fire a salute") for s in shots[:1]) if t]
