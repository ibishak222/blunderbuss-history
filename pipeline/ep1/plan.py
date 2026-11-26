"""Timeline: shots, chapter cards and effect events, shared by render.py and audio.py."""
import json, random, sys
sys.path.insert(0, "long")
from script import SCRIPT

timing = json.load(open("long/timing.json"))
DUR = timing[-1]["end"] + 1.5
CHAP_GAP = 2.2

TAGS = {
 "attack": "THE NORTH SEA · 22 OCTOBER 1904", "night_fleet": "THE DOGGER BANK · NORTH SEA", "port_arthur": "PORT ARTHUR · FEBRUARY 1904",
 "fleet_day": "THE SECOND PACIFIC SQUADRON", "rumours": "THE BALTIC · OCTOBER 1904", "kamchatka": "THE KAMCHATKA · 21 OCTOBER 1904",
 "crane": "THE TRAWLER CRANE", "aurora": "THE CRUISER AURORA", "hull": "HULL · OCTOBER 1904", "britain": "THE ROYAL NAVY",
 "vigo": "VIGO, SPAIN · NOVEMBER 1904", "madagascar": "NOSY BE, MADAGASCAR", "battle": "THE TSUSHIMA STRAIT · 27 MAY 1905",
 "tsushima": "THE BATTLE OF TSUSHIMA", "aurora_epi": "SAINT PETERSBURG · TODAY", "memorial": "HULL · 1906",
}

# merge consecutive paragraphs with the same shot into one continuous shot
shots = []
for i, p in enumerate(timing):
    start = p["start"] - (CHAP_GAP if p["chapter"] else 0)
    if shots and shots[-1]["shot"] == p["shot"] and not p["chapter"]:
        shots[-1]["paras"].append(p)
    else:
        shots.append({"shot": p["shot"], "start": start, "paras": [p], "chapter": p["chapter"], "para_start": p["start"]})
for i, s in enumerate(shots):
    s["end"] = shots[i + 1]["start"] if i + 1 < len(shots) else DUR
    s["idx"] = i
    s["sents"] = [x for p in s["paras"] for x in p["sents"]]

chapters = []
n = 0
for s in shots:
    if s["chapter"]:
        n += 1
        chapters.append((s["start"], s["para_start"], n, s["chapter"]))

def sent_time(shot, needle):
    for x in shot["sents"]:
        if needle.lower() in x["text"].lower():
            return x["start"]
    return None

# ---- gunfire / explosion events: (time, kind, x, y, scale, layer) in canvas coords (2400x1350) ----
# layer: "back" = on the back layer (moves with it, drawn behind the front layer)
#        "front" = in front-layer space but drawn behind front-layer objects (water splashes among boats)
#        "top" = in front-layer space, drawn on top (hits on foreground ships)
EVENTS = []
rng = random.Random(7)
ATTACK_SHIPS = [(150, 0.55), (520, 0.42), (820, 0.33), (1050, 0.26)]      # attack_back, waterline 764, bow right
AURORA_SHIPS = [(2150, 0.5), (1850, 0.38)]                               # aurora_back, flipped (bow left)
BATTLE_SHIPS = [(1700, 0.45), (1950, 0.4), (2200, 0.35)]                 # battle_back, flipped, waterline 822
def gun(x, s, wl, flip=False):
    return (x - 215 * s if flip else x + 215 * s, wl - 62 * s)
for s in shots:
    k, a, b = s["shot"], s["start"], s["end"]
    if k in ("attack", "crane"):
        f0 = sent_time(s, "open fire") or (a + 1.0)
        if k == "attack" and s["idx"] == 0:
            f0 = sent_time(s, "opened fire") or a + 6
        t = f0
        while t < b - 0.5:
            x, sc = rng.choice(ATTACK_SHIPS)
            gx, gy = gun(x, sc, 764)
            EVENTS.append((t, "muzzle", gx, gy, sc * 1.6, "back"))
            EVENTS.append((t + rng.uniform(0.6, 1.2), "splash", rng.choice([1000, 1320, 1780, 1950, 2200]), rng.choice([905, 935, 985]), rng.uniform(0.7, 1.0), "front"))
            t += rng.uniform(0.35, 1.3)
    if k == "aurora":
        t = a + 0.8
        while t < b - 0.5:
            x, sc = rng.choice(AURORA_SHIPS)
            gx, gy = gun(x, sc, 764, flip=True)
            EVENTS.append((t, "muzzle", gx, gy, sc * 1.6, "back"))
            if rng.random() < 0.45:
                EVENTS.append((t + 0.7, "hit", rng.choice([700, 820, 950, 1080]), rng.choice([900, 930]), 0.8, "top"))
            else:
                EVENTS.append((t + 0.8, "splash", rng.choice([500, 1350, 1500, 1650]), rng.choice([1000, 1040]), 0.9, "front"))
            t += rng.uniform(0.5, 1.6)
    if k == "port_arthur" and s is [x for x in shots if x["shot"] == "port_arthur"][0]:
        t = sent_time(s, "fired torpedoes") or a + 3
        for j in range(7):
            EVENTS.append((t + j * 1.3 + rng.uniform(0, 0.5), "hit", rng.choice([380, 600, 1080, 1320, 1850, 2050]), 862, 0.8, "top"))
    if k == "kamchatka":
        t = sent_time(s, "fired on them") or a + 4
        end = t + 9
        while t < min(b - 0.5, end):
            EVENTS.append((t, "muzzle", rng.choice([1560, 1700, 1900]), 945, 0.8, "top"))
            EVENTS.append((t + 0.8, "splash", rng.choice([300, 470, 650, 950]), 912, 0.4, "back"))
            t += rng.uniform(0.6, 1.4)
    if k == "battle" and s["chapter"]:
        t = a + 3
        while t < b - 0.5:
            x, sc = rng.choice(BATTLE_SHIPS)
            gx, gy = gun(x, sc, 822, flip=True)
            EVENTS.append((t, "muzzle", gx, gy, sc * 1.6, "back"))
            EVENTS.append((t + 0.9, "splash", rng.choice([300, 650, 1000, 1350]), rng.choice([905, 925]), 0.9, "front"))
            t += rng.uniform(0.8, 2.0)
EVENTS.sort()

# searchlights: origin on each ship's bridge (canvas coords of the back layer), aim angle in degrees (0 = right, + = down)
def lamp(x, s, wl, flip=False):
    return (x - 150 * s if flip else x + 150 * s, wl - 222 * s)
BEAMS = {
    "attack": [lamp(x, s, 764) + (ang, sp) for (x, s), ang, sp in zip(ATTACK_SHIPS, (9, 7, 6, 5), (0.5, 0.4, 0.6, 0.45))],
    "aurora": [lamp(x, s, 764, True) + (ang, sp) for (x, s), ang, sp in zip(AURORA_SHIPS, (172, 175), (0.45, 0.55))],
}
BEAMS["crane"] = BEAMS["attack"]
