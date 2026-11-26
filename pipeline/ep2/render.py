import math, os, subprocess, sys, glob, json
sys.path.insert(0, "ep2")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from plan import shots, chapters, DUR, TAGS, sent_time, FIRE, SCATTER, BURSTS
import random

FPS, OW, OH = 24, 1920, 1080
L = "ep2/layers/"
BASE = 0.8
_cache = {}
def img(n):
    if n not in _cache:
        _cache[n] = Image.open(L + n + ".png").convert("RGBA")
    return _cache[n]

FMONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
def mfont(size, w=b"Bold"):
    f = ImageFont.truetype(FMONT, size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
FSC = os.path.expanduser("~/.fonts/PlayfairSC-Black.ttf")
FPF = os.path.expanduser("~/.fonts/PlayfairDisplay.ttf")
def pfont(size, w=b"Black"):
    f = ImageFont.truetype(FPF, size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

PRESETS = [((1.0, 1200, 675), (1.12, 1230, 700)), ((1.1, 1330, 680), (1.1, 1070, 680)), ((1.14, 1200, 700), (1.0, 1200, 675)),
           ((1.1, 1070, 690), (1.1, 1330, 670)), ((1.04, 1150, 660), (1.16, 1260, 720))]
CAM_OVERRIDE = {"gunline": ((1.0, 1200, 700), (1.07, 1180, 720)), "dam": ((1.0, 1200, 690), (1.12, 1150, 740)),
                "emu_close": ((1.0, 1200, 660), (1.1, 1220, 640)), "truck": ((1.0, 1200, 675), (1.0, 1200, 675))}
def camera(s, t):
    (z0, x0, y0), (z1, x1, y1) = CAM_OVERRIDE.get(s["shot"], PRESETS[s["idx"] % len(PRESETS)])
    p = ease((t - s["start"]) / max(1, s["end"] - s["start"]))
    return z0 + (z1 - z0) * p, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p

def place(layer, z, cx, cy, out):
    a = 1.0 / (BASE * z)
    out.alpha_composite(layer.transform((OW, OH), Image.AFFINE, (a, 0, cx - OW / 2 * a, 0, a, cy - OH / 2 * a), resample=Image.BILINEAR))
def to_screen(x, y, z, cx, cy):
    k = BASE * z
    return (x - cx) * k + OW / 2, (y - cy) * k + OH / 2, k
def _paste_clip(out, sp, px, py):
    x0, y0 = max(0, px), max(0, py)
    x1, y1 = min(OW, px + sp.size[0]), min(OH, py + sp.size[1])
    if x1 <= x0 or y1 <= y0: return
    out.alpha_composite(sp.crop((x0 - px, y0 - py, x1 - px, y1 - py)), (x0, y0))
def paste_c(out, sp, x, y, alpha=1.0, anchor="c"):
    if alpha < 1:
        sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    px = int(x - sp.size[0] / 2)
    py = int(y - sp.size[1] / 2) if anchor == "c" else int(y - sp.size[1])
    _paste_clip(out, sp, px, py)

# ---------- emu sprites: feet anchor is (150, 430) in a 360x450 sprite ----------
_emu_cache = {}
def emu_sprite(pose, size, flip):
    key = (pose, size, flip)
    if key not in _emu_cache:
        im = img("emu_" + pose)
        h = max(4, int(450 * size)); w = max(4, int(360 * size))
        im = im.resize((w, h), Image.BILINEAR)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if len(_emu_cache) > 600: _emu_cache.clear()
        _emu_cache[key] = im
    return _emu_cache[key]
def draw_emu(out, x, y, sc, pose, flip, z, cx, cy):
    sx, sy, k = to_screen(x, y, z, cx, cy)
    size = round(sc * k * 20) / 20  # quantise for caching
    im = emu_sprite(pose, size, flip)
    ax = (360 - 150) * size if flip else 150 * size
    _paste_clip(out, im, int(sx - ax), int(sy - 430 * size))

def flock_members(seed, n, xr, yr, sr):
    r = random.Random(seed)
    m = [dict(x=r.uniform(*xr), y=r.uniform(*yr), s=r.uniform(*sr), ph=r.uniform(0, 10), sp=r.uniform(0.8, 1.3), flip=r.random() < 0.4) for _ in range(n)]
    return sorted(m, key=lambda e: e["y"])

def flock(out, t, z, cx, cy, members, mode_fn):
    """mode_fn(e, t) -> (x, y, pose, flip)"""
    for e in members:
        x, y, pose, flip = mode_fn(e, t)
        if -300 < x < 2800:
            draw_emu(out, x, y, e["s"], pose, flip, z, cx, cy)

def run_pose(t, rate=10):
    return "run" + str(int(t * rate) % 4)

def grazing(e, t):
    phase = (t * 0.4 + e["ph"]) % 4
    pose = "peck" if phase < 2.2 else "stand"
    return e["x"] + math.sin(t * 0.3 + e["ph"]) * 15, e["y"], pose, e["flip"]

def scatter(t0, speed=520, direction=1, run_for=2.6):
    """emus graze, bolt when the firing starts, then settle again further off (and the gun can't reach them)"""
    def f(e, t):
        if t < t0:
            return grazing(e, t)
        dt = t - t0 - (e["ph"] % 0.6)
        if dt < 0: return grazing(e, t)
        dd = min(dt, run_for)
        x = e["x"] + direction * speed * e["sp"] * dd * min(1, dd * 2.5)
        if dt < run_for:
            return x, e["y"] - abs(math.sin(dt * 9 + e["ph"])) * 6, run_pose(dt + e["ph"], 11), direction < 0
        return grazing(dict(e, x=x), t)
    return f

# ---------- effects ----------
def bursts_for(s, t):
    return [b for b in BURSTS if b[1] == s["idx"] and b[0] <= t < b[0] + 0.8]

def muzzle(out, t, s, mx, my, z, cx, cy, size=1.0):
    active = bursts_for(s, t)
    if not active: return 0
    flick = (int(t * 24) % 2 == 0)
    if flick:
        sx, sy, k = to_screen(mx, my, z, cx, cy)
        g = int(170 * k * size * (0.8 + 0.4 * random.random()))
        paste_c(out, img("flash").resize((g, g)), sx, sy)
    return 1

def dust_puffs(out, t, s, z, cx, cy, xr, yr):
    for (bt, idx) in BURSTS:
        if idx != s["idx"] or bt > t: continue
        for j in range(5):
            ti = bt + 0.15 + j * 0.13
            if 0 <= t - ti < 0.9:
                r = random.Random(int(bt * 100) + j)
                x, y = r.uniform(*xr), r.uniform(*yr)
                q = (t - ti) / 0.9
                sx, sy, k = to_screen(x, y, z, cx, cy)
                d = img("dust").resize((max(2, int(220 * k * (0.5 + q))), max(2, int(200 * k * (0.5 + q)))))
                paste_c(out, d, sx, sy, alpha=0.8 * (1 - q), anchor="b")

def rain(out, t):
    d = ImageDraw.Draw(out)
    r = random.Random(int(t * 24))
    for _ in range(260):
        x, y = r.randint(-100, OW), r.randint(-50, OH)
        d.line((x, y, x + 10, y + 46), fill=(200, 210, 220, 90), width=2)

def fan(out, t, z, cx, cy):
    sx, sy, k = to_screen(1650, 530, z, cx, cy)
    f = img("fan").rotate(-t * 70, resample=Image.BILINEAR)
    f = f.resize((int(280 * k), int(280 * k)))
    paste_c(out, f, sx, sy)

def rabbits(out, t, s, z, cx, cy):
    lt = t - s["start"]
    r = random.Random(s["idx"])
    for j in range(7):
        t0 = 1.0 + j * 1.6 + r.uniform(0, 0.8)
        if lt < t0: continue
        dt = lt - t0
        x = 1200 + (r.uniform(-60, 60)) + dt * 150 * (1 if j % 2 else -1) * 0.9
        y = 1020 + dt * 40 + j * 6
        hop = abs(math.sin(dt * 5)) * 40
        sx, sy, k = to_screen(x, y - hop, z, cx, cy)
        rb = img("rabbit").resize((max(2, int(140 * k * 0.9)), max(2, int(130 * k * 0.9))))
        if j % 2 == 0: rb = rb.transpose(Image.FLIP_LEFT_RIGHT)
        paste_c(out, rb, sx, sy, anchor="b")

# ---------- scene renderers ----------
FL_FIELD = flock_members(1, 6, (300, 2200), (1000, 1040), (0.55, 0.75))
FL_GUN = flock_members(2, 16, (1250, 1900), (880, 1000), (0.28, 0.45))
FL_DAM = flock_members(3, 34, (1500, 3400), (900, 1080), (0.3, 0.55))
FL_TRUCK = flock_members(4, 9, (1250, 1900), (960, 1140), (0.45, 0.65))
FL_LOOK = flock_members(5, 0, (0, 1), (0, 1), (0, 1))

def layered(out, t, s):
    k = s["shot"]
    z, cx, cy = camera(s, t)
    if k == "truck":
        truck_scene(out, t, s); return
    place(img(k + "_back"), z, cx, cy, out)
    lt = t - s["start"]
    if k == "emus_field":
        def walk(e, tt):
            x = e["x"] + (tt - s["start"]) * 60 * e["sp"] * (1 if e["flip"] else -1)
            return x, e["y"], run_pose(tt * 0.45 + e["ph"], 6), not e["flip"]
        flock(out, t, z, cx, cy, FL_FIELD[:3], walk)
    if k == "gunline":
        sc = SCATTER.get(s["idx"], 1e9)
        dust_puffs(out, t, s, z, cx, cy, (1300, 2300), (900, 1010))
        flock(out, t, z, cx, cy, FL_GUN, scatter(sc, 230))
    if k == "dam":
        f0 = FIRE[s["idx"]][0][0]; sc = SCATTER[s["idx"]]
        def dam_mode(e, tt):
            arrive = min(1, (tt - s["start"]) / max(2, f0 - s["start"]))
            tx = 1640 + (e["x"] - 1500) / 1900 * 680
            x = e["x"] - (e["x"] - tx) * ease(arrive)
            if tt < sc:
                if arrive < 1:
                    return x, e["y"], run_pose(tt * 0.5 + e["ph"], 6), True
                return grazing(dict(e, x=x), tt)
            dt = tt - sc - (e["ph"] % 0.6)
            if dt < 0: return x, e["y"], "stand", False
            return x + 520 * e["sp"] * dt * min(1, dt * 2.5), e["y"], run_pose(dt + e["ph"], 11), False
        dust_puffs(out, t, s, z, cx, cy, (1000, 1500), (930, 1060))
        flock(out, t, z, cx, cy, FL_DAM, dam_mode)
    if k == "lookout":
        ex, ey, es = 1800, 600, 0.6
        flip = (int((lt + 1) / 2.6) % 2 == 1)
        draw_emu(out, ex, ey, es, "stand", flip, z, cx, cy)
    if k == "emu_close":
        bob = math.sin(lt * 1.3) * 6
        pose = "peck" if (lt % 9) > 7.2 else "stand"
        draw_emu(out, 1250, 1080 + bob * 0, 1.9, pose, False, z, cx, cy)
    if k == "farm":
        fan(out, t, z, cx, cy)
    if k == "fence":
        rabbits(out, t, s, z, cx, cy)
    front = img(k + "_front")
    place(front, z, cx, cy, out)
    if k == "gunline":
        muzzle(out, t, s, 330 + 210 * 1.05, 1180 - 62 * 1.05, z, cx, cy, 1.2)
    if k == "dam":
        muzzle(out, t, s, 300 + 210 * 0.9, 1110 - 62 * 0.9, z, cx, cy, 1.0)
    if k == "rain":
        rain(out, t)

def truck_scene(out, t, s):
    lt = t - s["start"]
    out.alpha_composite(img("truck_back").resize((OW, OH)))
    g = img("truck_ground").resize((OW, OH))
    off = int((lt * 420) % OW)
    out.alpha_composite(g, (-off, 0)); out.alpha_composite(g, (OW - off, 0))
    # emus ahead, pulling away
    for e in FL_TRUCK:
        x = e["x"] + lt * 40 * e["sp"]
        y = e["y"] - abs(math.sin(lt * 9 + e["ph"])) * 8
        draw_emu(out, x, y, e["s"], run_pose(lt + e["ph"], 11), False, 1.0, 1200, 675)
    # truck: drifts back as emus pull ahead, bouncing hard
    tx = 520 - lt * 6
    bounce = abs(math.sin(lt * 7.3)) * 14 + math.sin(lt * 13.1) * 5
    tilt = math.sin(lt * 5.1) * 2.5
    tr = img("truck").rotate(tilt, resample=Image.BILINEAR, center=(330, 420))
    sx, sy, k = to_screen(tx, 1160 - bounce, 1.0, 1200, 675)
    trs = tr.resize((int(680 * k * 1.05), int(440 * k * 1.05)))
    _paste_clip(out, trs, int(sx - 330 * k * 1.05), int(sy - 420 * k * 1.05))
    # dust behind the truck
    for j in range(4):
        q = ((lt * 1.3 + j / 4) % 1)
        dx, dy, kk = to_screen(tx - 330 - q * 300, 1150 - q * 40, 1.0, 1200, 675)
        d = img("dust").resize((max(2, int(260 * kk * (0.6 + q))), max(2, int(200 * kk * (0.6 + q)))))
        paste_c(out, d, dx, dy, alpha=0.7 * (1 - q), anchor="b")
    # gun on the cab roof: muzzle in truck sprite coords (330-90+0.7*210, 420-190-0.7*62) relative to (330,420)
    mx = tx + (-90 + 0.7 * 210) * 1.05 * 1.0
    my = 1160 - bounce + (-190 - 0.7 * 62) * 1.05
    muzzle(out, t, s, mx, my, 1.0, 1200, 675, 0.9)

def paper_scene(out, t, s, name, stamp_at=None):
    lt = t - s["start"]
    out.alpha_composite(img("desk").resize((OW, OH)))
    D = max(4, s["end"] - s["start"])
    z = 0.9 + 0.1 * ease(lt / D)
    p = img(name)
    pw, ph = int(p.size[0] * 0.62 * z), int(p.size[1] * 0.62 * z)
    pp = p.resize((pw, ph), Image.BILINEAR).rotate(-2 + 2 * ease(lt / 1.2), resample=Image.BILINEAR, expand=True)
    x, y = OW // 2 - pp.size[0] // 2, int(OH / 2 - pp.size[1] / 2 + 140 - 260 * ease(lt / D))
    sh = Image.new("RGBA", pp.size, (0, 0, 0, 0)); sh.putalpha(pp.getchannel("A").point(lambda v: v // 2))
    _paste_clip(out, sh.filter(ImageFilter.GaussianBlur(14)), x + 18, y + 26)
    _paste_clip(out, pp, x, y)
    if stamp_at and t >= stamp_at:
        k = ease((t - stamp_at) / 0.16)
        sc = 1.6 - 0.75 * k
        st = img("stamp").resize((int(720 * sc), int(340 * sc)))
        paste_c(out, st, OW // 2 + 180, OH // 2 + 120, alpha=k)

WP = {"Perth": (560, 900), "Chandler": (1150, 600), "Campion": (1380, 540), "Walgoolan": (1320, 760)}
FL = mfont(32, b"Bold")
def map_scene(out, t, s):
    place(img("map_back"), 1.0, 1200, 675, out)
    d = ImageDraw.Draw(out)
    S = lambda p: (p[0] * BASE, p[1] * BASE)
    lt = t - s["start"]
    # migration: dotted streams flowing in from the north and east
    for (sx0, sy0), (ex, ey) in [((2000, 200), (1380, 540)), ((2250, 700), (1320, 760)), ((1700, 120), (1150, 600))]:
        for j in range(14):
            q = ((lt * 0.12 + j / 14) % 1)
            x, y = sx0 + (ex - sx0) * q, sy0 + (ey - sy0) * q
            a, b = S((x, y))
            d.ellipse((a - 7, b - 7, a + 7, b + 7), fill=(122, 74, 40, int(230 * min(1, lt / 1.5))))
    for name, p in WP.items():
        x, y = S(p)
        col = (217, 72, 43, 255) if name != "Perth" else (20, 32, 46, 255)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col)
        d.text((x + 18, y - 4), name.upper(), font=FL, fill=col, anchor="lm")
    a, b = S((1900, 300))
    d.text((a, b), "~20,000 EMUS", font=mfont(40, b"ExtraBold"), fill=(122, 74, 40, int(255 * min(1, lt / 1.5))), anchor="mm")

def title_scene(out, t, s):
    place(img("emus_field_back"), 1.05, 1200, 675, out); place(img("emus_field_front"), 1.05, 1200, 675, out)
    out.alpha_composite(Image.new("RGBA", (OW, OH), (20, 10, 8, 150)))
    lt = t - s["start"]; k = ease(lt / 1.0)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 470), "THE GREAT EMU WAR", font=ImageFont.truetype(FSC, 140), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 590), "Western Australia, 1932: soldiers vs. emus", font=pfont(48, b"Bold"), fill=(255, 201, 74, int(255 * k)), anchor="mm")
    d.line((760, 650, 1160, 650), fill=(217, 72, 43, int(255 * k)), width=4)

LOGO = Image.open("brand/logo_icon.png").convert("RGBA").resize((420, 420), Image.LANCZOS)
_m = Image.new("L", (420, 420), 0); ImageDraw.Draw(_m).ellipse((0, 0, 419, 419), fill=255); LOGO.putalpha(_m)
def outro(out, t, s):
    out.alpha_composite(Image.new("RGBA", (OW, OH), (20, 32, 46, 255)))
    lt = t - s["start"]; k = ease(lt / 0.6)
    paste_c(out, LOGO, OW / 2, 400, alpha=k)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 690), "BLUNDERBUSS HISTORY", font=ImageFont.truetype(FSC, 90), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 775), "The full stories of history's biggest blunders", font=mfont(38, b"SemiBold"), fill=(201, 160, 74, int(255 * k)), anchor="mm")
    d.rounded_rectangle((OW / 2 - 200, 840, OW / 2 + 200, 920), 40, fill=(217, 72, 43, int(255 * k)))
    d.text((OW / 2, 881), "SUBSCRIBE", font=mfont(40, b"ExtraBold"), fill=(241, 228, 200, int(255 * k)), anchor="mm")

FT = mfont(28, b"ExtraBold")
_tags = {}
def tag_img(text):
    if text not in _tags:
        w = int(FT.getlength(text)) + 60
        im = Image.new("RGBA", (w, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, 59), 30, fill=(20, 32, 46, 220), outline=(201, 160, 74, 255), width=3)
        d.text((w // 2, 31), text, font=FT, fill=(241, 228, 200), anchor="mm")
        _tags[text] = im
    return _tags[text]

FCH1 = mfont(34, b"Bold")
def chapter_card(out, t):
    for (a, ps, n, title) in chapters:
        if a <= t < ps + 1.2:
            k = min(ease((t - a) / 0.4), 1 - ease((t - (ps + 0.6)) / 0.6))
            out.alpha_composite(Image.new("RGBA", (OW, OH), (10, 14, 22, int(215 * k))))
            d = ImageDraw.Draw(out)
            d.text((OW / 2, 470), f"CHAPTER {n}", font=FCH1, fill=(201, 160, 74, int(255 * k)), anchor="mm")
            fsz = 92
            while ImageFont.truetype(FSC, fsz).getlength(title.upper()) > 1680: fsz -= 4
            d.text((OW / 2, 560), title.upper(), font=ImageFont.truetype(FSC, fsz), fill=(241, 228, 200, int(255 * k)), anchor="mm")
            d.line((OW / 2 - 120, 630, OW / 2 + 120, 630), fill=(217, 72, 43, int(255 * k)), width=4)

# ---------- captions (same style as episode 1) ----------
REPL = [("nineteen thirty-two", "1932"), ("nineteen thirty-three", "1933"), ("nineteen thirty-four", "1934"), ("nineteen forty-three", "1943"),
        ("nineteen forty-eight", "1948"), ("nineteen fifty", "1950"), ("nineteen twenty-nine", "1929"), ("twenty twenty-three", "2023"),
        ("nine hundred and eighty-six", "986"), ("nine thousand eight hundred and sixty", "9,860"), ("two and a half thousand", "2,500"),
        ("fifty-seven thousand", "57,000"), ("twenty thousand", "20,000"), ("ten thousand", "10,000"), ("two hundred thousand", "200,000"),
        ("half a million", "500,000"), ("fifty kilometres an hour", "50 km/h"), ("three hundred", "300"), ("a hundred", "100"),
        ("second of November", "2nd of November"), ("eighth of November", "8th of November"), ("twelfth of November", "12th of November"),
        ("tenth of December", "10th of December")]
_tim = json.load(open("ep2/timing.json"))
CAPS = []
for p in _tim:
    for st in p["sents"]:
        txt = st["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a[0].upper() + a[1:], b)
        words = txt.split(); groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 4 or (w[-1] in ".,?!;:" and len(cur) >= 2):
                groups.append(cur); cur = []
        if cur:
            if groups and len(cur) == 1: groups[-1] += cur
            else: groups.append(cur)
        tot = sum(len(w) + 1 for w in words); acc = st["start"]; dur = st["end"] - st["start"]
        for g in groups:
            wt = []
            for w in g:
                d_ = dur * (len(w) + 1) / tot; wt.append((acc, acc + d_)); acc += d_
            CAPS.append((wt[0][0], wt[-1][1], g, wt))
ANTON = glob.glob("/usr/share/fonts/**/Anton*.ttf", recursive=True)[0]
_fonts = {}
def capfont(sz):
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(ANTON, sz)
    return _fonts[sz]
BASE_SZ = 70
_layout = {}
def layout(ci):
    if ci not in _layout:
        g = [w.upper() for w in CAPS[ci][2]]
        f = capfont(BASE_SZ); sp = f.getlength(" ") * 1.9
        ws = [f.getlength(w) for w in g]; xs, x = [], 0
        for wd in ws: xs.append(x); x += wd + sp
        _layout[ci] = (g, ws, xs, x - sp)
    return _layout[ci]
_band = np.zeros((OH, OW, 4), np.uint8)
for y in range(780, OH):
    _band[y, :, 3] = int(150 * ((y - 780) / (OH - 780)) ** 1.3)
BAND = Image.fromarray(_band, "RGBA")
CREAMC, GOLD = (241, 228, 200), (255, 201, 74)
def captions(out, t, s):
    if s["shot"] in ("title", "outro"): return
    for ci, (a, b, g, wt) in enumerate(CAPS):
        if a - 0.05 <= t < b + 0.18:
            words, ws, xs, total = layout(ci)
            k_in = ease((t - a + 0.05) / 0.18); k_out = 1 - ease((t - b) / 0.18); vis = min(k_in, k_out)
            if vis > 0: out.alpha_composite(BAND)
            Wc, Hc = int(total) + 120, 170
            lay = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for j, (w, wd, x0) in enumerate(zip(words, ws, xs)):
                w0, w1 = wt[j]; cxw = 60 + x0 + wd / 2
                if t < w0: col, sz, lift = CREAMC + (95,), BASE_SZ, 0
                elif t < w1 + 0.02:
                    p = ease((t - w0) / 0.12); sz = int(BASE_SZ * (1.03 + 0.12 * (1 - p))); col, lift = GOLD + (255,), -6 * p
                else: col, sz, lift = CREAMC + (255,), BASE_SZ, 0
                d.text((cxw, Hc / 2 + lift), w, font=capfont(sz), fill=col, anchor="mm", stroke_width=3, stroke_fill=(10, 12, 18, col[3]))
            sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.75)))
            sh = sh.filter(ImageFilter.GaussianBlur(7))
            comp = Image.new("RGBA", lay.size, (0, 0, 0, 0)); comp.alpha_composite(sh, (0, 4)); comp.alpha_composite(lay)
            if vis < 1: comp.putalpha(comp.getchannel("A").point(lambda v: int(v * vis)))
            paste_c(out, comp, OW / 2, 960 + 18 * (1 - k_in))
            return

yy, xx = np.mgrid[0:OH, 0:OW]
r = np.sqrt(((xx - OW / 2) / (OW * 0.72)) ** 2 + ((yy - OH / 2) / (OH * 0.72)) ** 2)
VIG = Image.fromarray(np.dstack([np.zeros_like(r)] * 3 + [np.clip((r - 0.6) * 320, 0, 160)]).astype(np.uint8), "RGBA")

LAYERED = {"gunline", "emus_field", "trenches", "farm", "emu_close", "fence", "gun_crew", "rain", "dam", "lookout", "truck", "coat"}
def frame(t):
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[0] if t < shots[0]["start"] else shots[-1])
    k = s["shot"]
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    random.seed(int(t * FPS))
    if k in LAYERED: layered(out, t, s)
    elif k == "wa_map": map_scene(out, t, s)
    elif k in ("paper_a", "paper_b", "paper_c", "report"):
        st = sent_time(s, "Exactly ten bullets") if k == "report" else None
        paper_scene(out, t, s, k, st)
    elif k == "title": title_scene(out, t, s)
    elif k == "outro": outro(out, t, s)
    out.alpha_composite(VIG)
    if t - s["start"] < 0.15 and s["idx"] > 0 and not s["chapter"]:
        out.alpha_composite(Image.new("RGBA", (OW, OH), (255, 255, 255, int(90 * (1 - (t - s["start"]) / 0.15)))))
    if k in TAGS:
        a = s["para_start"] + 0.3
        if t >= a:
            q = ease((t - a) / 0.4) * (1 - ease((t - (a + 7)) / 0.5))
            if q > 0:
                ti = tag_img(TAGS[k]); ti2 = ti.copy(); ti2.putalpha(ti.getchannel("A").point(lambda v: int(v * q)))
                out.alpha_composite(ti2, (60, 50))
    chapter_card(out, t)
    captions(out, t, s)
    if t < 0.8 or t > DUR - 1.0:
        f = ease(t / 0.8) if t < 0.8 else ease((DUR - t) / 1.0)
        out.alpha_composite(Image.new("RGBA", (OW, OH), (0, 0, 0, int(255 * (1 - f)))))
    return out.convert("RGB")

NF = int(DUR * FPS)
if __name__ == "__main__":
    if sys.argv[1] == "preview":
        for tt in sys.argv[2].split(","):
            frame(float(tt)).save(f"ep2/prev_{tt}.jpg", quality=85)
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"ep2/part{part}.mp4"], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 500 == 0: print(part, i, b, flush=True)
    p.stdin.close(); p.wait()
    print("part", part, "done", flush=True)
