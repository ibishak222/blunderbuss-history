import math, os, subprocess, sys, glob
sys.path.insert(0, "long")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from plan import shots, chapters, EVENTS, DUR, TAGS, sent_time, BEAMS

FPS, OW, OH = 24, 1920, 1080
L = "long/layers/"
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

def camera(s, t):
    (z0, x0, y0), (z1, x1, y1) = PRESETS[s["idx"] % len(PRESETS)]
    p = ease((t - s["start"]) / max(1, s["end"] - s["start"]))
    return z0 + (z1 - z0) * p, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p

def place(layer, z, cx, cy, out):
    a = 1.0 / (BASE * z)
    out.alpha_composite(layer.transform((OW, OH), Image.AFFINE, (a, 0, cx - OW / 2 * a, 0, a, cy - OH / 2 * a), resample=Image.BILINEAR))

def to_screen(x, y, z, cx, cy):
    k = BASE * z
    return (x - cx) * k + OW / 2, (y - cy) * k + OH / 2, k

def paste_c(out, sp, x, y, alpha=1.0, anchor="c"):
    if alpha < 1:
        sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    px = int(x - sp.size[0] / 2)
    py = int(y - sp.size[1] / 2) if anchor == "c" else int(y - sp.size[1])
    out.alpha_composite(sp, (px, py)) if (px > -sp.size[0] and py > -sp.size[1] and px < OW and py < OH) and px >= 0 and py >= 0 else _paste_clip(out, sp, px, py)

def _paste_clip(out, sp, px, py):
    x0, y0 = max(0, px), max(0, py)
    x1, y1 = min(OW, px + sp.size[0]), min(OH, py + sp.size[1])
    if x1 <= x0 or y1 <= y0: return
    out.alpha_composite(sp.crop((x0 - px, y0 - py, x1 - px, y1 - py)), (x0, y0))

def draw_events(out, t, zl, cx, cy, s, stage):
    """stage: 'back' (events on the back layer, zl = back zoom), 'front', 'top' (front zoom)."""
    flash_total = 0
    for (et, kind, x, y, sc, layer) in EVENTS:
        if et > t: break
        if layer != stage or not (s["start"] <= et < s["end"]): continue
        sx, sy, k = to_screen(x, y, zl, cx, cy)
        if kind in ("muzzle", "hit") and t - et < 0.25:
            q = 1 - (t - et) / 0.25
            size = int(300 * k * sc * (0.5 + q) * (1.5 if kind == "hit" else 1))
            paste_c(out, img("flash").resize((max(2, size), max(2, size))), sx, sy)
        if kind in ("splash", "hit") and 0 <= t - et - (0.1 if kind == "hit" else 0) < 1.0:
            q = (t - et) / 1.0
            h = int(330 * k * sc * (0.3 + 0.9 * math.sin(min(1, q * 1.4) * math.pi / 2)))
            w = int(300 * k * sc * 0.7)
            if h > 2 and w > 2:
                paste_c(out, img("splash").resize((w, h)), sx, sy, alpha=1 - q, anchor="b")

def scene_flash(out, t, s):
    f = 0
    for (et, kind, x, y, sc, layer) in EVENTS:
        if et > t: break
        if s["start"] <= et < s["end"] and kind in ("muzzle", "hit") and t - et < 0.2:
            f = max(f, (1 - (t - et) / 0.2) * (0.3 if kind == "muzzle" else 0.45))
    if f > 0:
        out.alpha_composite(Image.new("RGBA", (OW, OH), (255, 200, 140, int(110 * f))))

_beam_small = None
def beams(out, t, zl, cx, cy, s, sources):
    """Searchlights drawn exactly from their lamp: sprite origin (0,200) mapped to the lamp's screen point."""
    global _beam_small
    if not sources: return
    lt = t - s["start"]
    on = ease(lt / 0.8)
    spr = img("beam")
    for i, (ox, oy, base, sp) in enumerate(sources):
        sx, sy, k = to_screen(ox, oy, zl, cx, cy)
        th = math.radians(base + 5 * math.sin(lt * sp + i * 1.7))
        c, sn = math.cos(th), math.sin(th)
        kk = k * 1.15
        data = (c / kk, sn / kk, -(c * sx + sn * sy) / kk, -sn / kk, c / kk, (sn * sx - c * sy) / kk + 200)
        bm = spr.transform((OW, OH), Image.AFFINE, data, resample=Image.BILINEAR)
        if on < 1:
            bm.putalpha(bm.getchannel("A").point(lambda v: int(v * on)))
        out.alpha_composite(bm)
        g = max(4, int(70 * k))  # the lamp itself
        paste_c(out, img("flash").resize((g, g)), sx, sy, alpha=0.9 * on)

def scene_layers(name):
    return img(name + "_back"), img(name + "_front")

def paper_scene(out, t, s, name, stamp_at=None):
    lt = t - s["start"]
    out.alpha_composite(img("desk").resize((OW, OH)))
    z = 0.9 + 0.1 * ease(lt / max(4, s["end"] - s["start"]))
    p = img(name)
    pw, ph = int(p.size[0] * 0.62 * z), int(p.size[1] * 0.62 * z)
    pp = p.resize((pw, ph), Image.BILINEAR).rotate(-2 + 2 * ease(lt / 1.2), resample=Image.BILINEAR, expand=True)
    x, y = OW // 2 - pp.size[0] // 2, int(OH / 2 - pp.size[1] / 2 + 140 - 260 * ease(lt / max(4, s["end"] - s["start"])))
    sh = Image.new("RGBA", pp.size, (0, 0, 0, 0)); sh.putalpha(pp.getchannel("A").point(lambda v: v // 2))
    _paste_clip(out, sh.filter(ImageFilter.GaussianBlur(14)), x + 18, y + 26)
    _paste_clip(out, pp, x, y)
    if stamp_at and t >= stamp_at:
        k = ease((t - stamp_at) / 0.16)
        sc = 1.6 - 0.75 * k
        st = img("stamp").resize((int(680 * sc), int(330 * sc)))
        paste_c(out, st, OW // 2 + 200, OH // 2 + 150, alpha=k)

TEL_POS = [(430, 280, -5), (960, 300, 4), (1490, 270, -3), (440, 700, 4), (970, 690, -4), (1500, 700, 3)]
def rumours(out, t, s):
    out.alpha_composite(img("desk").resize((OW, OH)))
    lt, D = t - s["start"], s["end"] - s["start"]
    for i, (x, y, r) in enumerate(TEL_POS):
        ti = 0.8 + i * (D - 3) / 6
        if lt < ti: break
        k = ease((lt - ti) / 0.35)
        tel = img(f"tel{i}")
        sc = 0.66 * (1.25 - 0.25 * k)
        tm = tel.resize((int(tel.size[0] * sc), int(tel.size[1] * sc))).rotate(r, expand=True, resample=Image.BILINEAR)
        paste_c(out, tm, x, y + (1 - k) * 40, alpha=k)

# ---- map ----
WP = {"Libau": (760, 300), "Dogger Bank": (560, 370), "Vigo": (390, 560), "Tangier": (450, 690), "Suez": (930, 650),
      "Cape of Good Hope": (820, 1180), "Madagascar": (1180, 1010), "Cam Ranh": (1820, 760), "Tsushima": (2040, 470),
      "Vladivostok": (2160, 320), "Port Arthur": (1900, 400)}
ROUTE_MAIN = ["Libau", "Dogger Bank", "Vigo", "Tangier", (500, 900), "Cape of Good Hope", "Madagascar", (1500, 950), "Cam Ranh", "Tsushima"]
ROUTE_SUEZ = ["Tangier", (700, 690), "Suez", (1050, 800), "Madagascar"]
PROG = {"map_a": None, "map_b": (0.0, 0.12), "map_c": (0.12, 0.66), "map_d": (0.66, 1.0)}
FL = mfont(30, b"Bold"); FLB = pfont(40, b"Black")
def poly(names):
    return [WP[n] if isinstance(n, str) else n for n in names]
def partial(pts, frac):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot, goal, out = sum(seg), sum(seg) * frac, [pts[0]]
    acc = 0
    for i, d in enumerate(seg):
        if acc + d >= goal:
            r = (goal - acc) / d if d else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r)); return out
        out.append(pts[i + 1]); acc += d
    return out
def map_scene(out, t, s):
    place(img("map_back"), 1.0, 1200, 675, out)
    d = ImageDraw.Draw(out)
    S = lambda p: (p[0] * BASE, p[1] * BASE)
    prog = PROG[s["shot"]]
    lt, D = t - s["start"], s["end"] - s["start"]
    main = poly(ROUTE_MAIN)
    # faint full route
    for a, b in zip(main, main[1:]):
        d.line([S(a), S(b)], fill=(90, 70, 48, 70), width=4)
    if prog:
        f = prog[0] + (prog[1] - prog[0]) * ease((lt - 0.5) / max(1, D - 2))
        pts = partial(main, f)
        d.line([S(p) for p in pts], fill=(217, 72, 43, 255), width=9, joint="curve")
        if f > 0.42:  # Suez detachment
            sz = poly(ROUTE_SUEZ)
            sf = min(1, (f - 0.42) / 0.2)
            d.line([S(p) for p in partial(sz, sf)], fill=(201, 120, 60, 255), width=6, joint="curve")
        hx, hy = S(pts[-1])
        d.ellipse((hx - 16, hy - 16, hx + 16, hy + 16), fill=(20, 32, 46, 255), outline=(241, 228, 200, 255), width=4)
    for name, p in WP.items():
        x, y = S(p)
        col = (20, 32, 46, 255)
        if name == "Port Arthur":
            pulse = 10 + 6 * math.sin(t * 4)
            d.ellipse((x - pulse * 2, y - pulse * 2, x + pulse * 2, y + pulse * 2), outline=(217, 72, 43, 180), width=3)
            col = (217, 72, 43, 255)
        if name == "Dogger Bank":
            col = (217, 72, 43, 255)
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=col)
        if name in ("Vladivostok", "Tsushima", "Cam Ranh"):
            d.text((x - 16, y - 4), name.upper(), font=FL, fill=col, anchor="rm")
        else:
            d.text((x + 16, y - 4), name.upper(), font=FL, fill=col, anchor="lm")
    for txt, p in [("EUROPE", (420, 200)), ("AFRICA", (700, 900)), ("ASIA", (1500, 300)), ("JAPAN", (2130, 560)), ("INDIAN OCEAN", (1350, 1110))]:
        d.text(S(p), txt, font=FLB, fill=(90, 70, 48, 150), anchor="mm")

def title_scene(out, t, s):
    place(img("night_fleet_back"), 1.05, 1200, 675, out); place(img("night_fleet_front"), 1.08, 1200, 675, out)
    out.alpha_composite(Image.new("RGBA", (OW, OH), (8, 12, 20, 150)))
    lt = t - s["start"]; k = ease(lt / 1.0)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 430), "THE DOGGER BANK", font=ImageFont.truetype(FSC, 130), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 570), "INCIDENT", font=ImageFont.truetype(FSC, 130), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 680), "The night the Russian Navy attacked a fishing fleet", font=pfont(46, b"Bold"), fill=(201, 160, 74, int(255 * k)), anchor="mm")
    d.line((760, 740, 1160, 740), fill=(217, 72, 43, int(255 * k)), width=4)

LOGO = Image.open("brand/logo_icon.png").convert("RGBA").resize((420, 420), Image.LANCZOS)
_m = Image.new("L", (420, 420), 0); ImageDraw.Draw(_m).ellipse((0, 0, 419, 419), fill=255); LOGO.putalpha(_m)
def outro(out, t, s):
    out.alpha_composite(Image.new("RGBA", (OW, OH), (20, 32, 46, 255)))
    lt = t - s["start"]; k = ease(lt / 0.6)
    paste_c(out, LOGO, OW / 2, 400, alpha=k)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 690), "BLUNDERBUSS HISTORY", font=ImageFont.truetype(FSC, 90), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 775), "The full stories of history's biggest blunders", font=mfont(38, b"SemiBold"), fill=(201, 160, 74, int(255 * k)), anchor="mm")
    bx = OW / 2
    d.rounded_rectangle((bx - 200, 840, bx + 200, 920), 40, fill=(217, 72, 43, int(255 * k)))
    d.text((bx, 881), "SUBSCRIBE", font=mfont(40, b"ExtraBold"), fill=(241, 228, 200, int(255 * k)), anchor="mm")

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

FCH1, FCH2 = mfont(34, b"Bold"), ImageFont.truetype(FSC, 92)
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


# ---------- dynamic captions ----------
import json as _json
FCAP = ImageFont.truetype(glob.glob("/usr/share/fonts/**/Anton*.ttf", recursive=True)[0], 66)
REPL = [("nineteen-oh-four", "1904"), ("nineteen-oh-five", "1905"), ("nineteen-oh-six", "1906"), ("nineteen seventeen", "1917"),
        ("sixty-six thousand pounds", "£66,000"), ("eighteen thousand", "18,000"), ("twenty-eight", "28"), ("three hundred", "300"),
        ("five hundred", "500"), ("five thousand", "5,000"), ("a hundred and seventeen", "117"), ("twenty-seventh", "27th"),
        ("twenty-second", "22nd"), ("twenty-first", "21st"), ("fifteenth", "15th"), ("sixteenth", "16th"), ("eleventh", "11th"),
        ("fifth of September", "5th of September"), ("second of January", "2nd of January"), ("first of November", "1st of November")]
KEY = {"russian", "russia", "japan", "japanese", "britain", "british", "hull", "dogger", "bank", "crane", "aurora", "kamchatka", "tsushima",
       "rozhestvensky", "togo", "nebogatov", "madagascar", "torpedo", "fishermen", "fire.", "fire", "war", "war.", "1904", "1905", "£66,000",
       "port", "arthur", "libau", "vigo", "paris", "pirates.", "outrage.", "catastrophe.", "1917", "18,000", "500", "300", "5,000", "117"}
_tim = _json.load(open("long/timing.json"))
CAPS = []  # (start, end, words, word_times)
for p in _tim:
    for st in p["sents"]:
        txt = st["text"]
        for a, b in REPL: txt = txt.replace(a, b).replace(a[0].upper() + a[1:], b)
        words = txt.split()
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 4 or w[-1] in ".,?!;:" and len(cur) >= 2:
                groups.append(cur); cur = []
        if cur:
            if groups and len(cur) == 1: groups[-1] += cur
            else: groups.append(cur)
        tot = sum(len(w) + 1 for w in words)
        acc = st["start"]; dur = st["end"] - st["start"]
        for g in groups:
            wt = []
            for w in g:
                d = dur * (len(w) + 1) / tot
                wt.append((acc, acc + d)); acc += d
            CAPS.append((wt[0][0], wt[-1][1], g, wt))
_fonts = {}
def capfont(sz):
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(glob.glob("/usr/share/fonts/**/Anton*.ttf", recursive=True)[0], sz)
    return _fonts[sz]
BASE_SZ = 70
_layout = {}
def layout(ci):
    if ci not in _layout:
        g = [w.upper() for w in CAPS[ci][2]]
        f = capfont(BASE_SZ); sp = f.getlength(" ") * 1.45
        ws = [f.getlength(w) for w in g]
        xs, x = [], 0
        for wd in ws: xs.append(x); x += wd + sp
        _layout[ci] = (g, ws, xs, x - sp)
    return _layout[ci]
# soft band behind captions so they sit in the picture instead of on top of it
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
            k_in = ease((t - a + 0.05) / 0.18); k_out = 1 - ease((t - b) / 0.18)
            vis = min(k_in, k_out)
            out.alpha_composite(BAND) if vis > 0 else None
            Wc, Hc = int(total) + 120, 170
            lay = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for j, (w, wd, x0) in enumerate(zip(words, ws, xs)):
                w0, w1 = wt[j]
                cx = 60 + x0 + wd / 2
                if t < w0:      # not spoken yet: faint
                    col, sz, lift = CREAMC + (95,), BASE_SZ, 0
                elif t < w1 + 0.02:  # being spoken: pop in gold
                    p = ease((t - w0) / 0.12)
                    sz = int(BASE_SZ * (1.0 + 0.16 * (1 - p) + 0.06))
                    col, lift = GOLD + (255,), -6 * p
                else:           # spoken
                    col, sz, lift = CREAMC + (255,), BASE_SZ, 0
                d.text((cx, Hc / 2 + lift), w, font=capfont(sz), fill=col, anchor="mm", stroke_width=3, stroke_fill=(10, 12, 18, col[3]))
            sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.75)))
            sh = sh.filter(ImageFilter.GaussianBlur(7))
            comp = Image.new("RGBA", lay.size, (0, 0, 0, 0)); comp.alpha_composite(sh, (0, 4)); comp.alpha_composite(lay)
            if vis < 1: comp.putalpha(comp.getchannel("A").point(lambda v: int(v * vis)))
            y = 960 + 18 * (1 - k_in)
            paste_c(out, comp, OW / 2, y)
            return

yy, xx = np.mgrid[0:OH, 0:OW]
r = np.sqrt(((xx - OW / 2) / (OW * 0.72)) ** 2 + ((yy - OH / 2) / (OH * 0.72)) ** 2)
VIG = Image.fromarray(np.dstack([np.zeros_like(r)] * 3 + [np.clip((r - 0.6) * 320, 0, 160)]).astype(np.uint8), "RGBA")

LAYERED = {"night_fleet", "attack", "crane", "aurora", "port_arthur", "fleet_day", "britain", "battle", "kamchatka", "hull", "vigo",
           "madagascar", "tsushima", "aurora_epi", "memorial"}
def frame(t):
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[0] if t < shots[0]["start"] else shots[-1])
    k = s["shot"]
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    if k in LAYERED:
        z, cx, cy = camera(s, t)
        name = {"crane": "attack", "britain": "fleet_day"}.get(k, k)
        back = img(name + "_back")
        front = img(("britain" if k == "britain" else name) + "_front")
        zb = z  # same depth: objects resting on the water must stay locked to it
        place(back, zb, cx, cy, out)
        beams(out, t, zb, cx, cy, s, BEAMS.get(k, []))
        draw_events(out, t, zb, cx, cy, s, "back")
        draw_events(out, t, z, cx, cy, s, "front")
        place(front, z, cx, cy, out)
        if k == "crane":
            lt = t - s["start"]
            sink = ease((lt - 1.0) / max(3, (s["end"] - s["start"]) * 0.45))
            ang = 2.0 * math.sin(lt * 1.6) + 24 * sink
            cr = img("crane").rotate(ang, resample=Image.BILINEAR, center=(380, 430))
            dy = sink * 210 + 6 * math.sin(lt * 1.3)
            cr = cr.crop((0, 0, 760, max(2, int(430 + 12 - dy))))
            sx, sy, kk = to_screen(700, 1060 + dy, z, cx, cy)
            crs = cr.resize((max(2, int(cr.size[0] * kk)), max(2, int(cr.size[1] * kk))))
            _paste_clip(out, crs, int(sx - 380 * kk), int(sy - 430 * kk))
        draw_events(out, t, z, cx, cy, s, "top")
        scene_flash(out, t, s)
    elif k.startswith("map"):
        map_scene(out, t, s)
    elif k == "rumours":
        rumours(out, t, s)
    elif k in ("paper1", "paper2", "treaty", "court"):
        st = sent_time(s, "sixty-six") if k == "paper2" else None
        paper_scene(out, t, s, k, (st + 1.6) if st else None)
    elif k == "title":
        title_scene(out, t, s)
    elif k == "outro":
        outro(out, t, s)
    out.alpha_composite(VIG)
    # cut flash
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
    # fade in/out
    if t < 0.8 or t > DUR - 1.0:
        f = ease(t / 0.8) if t < 0.8 else ease((DUR - t) / 1.0)
        out.alpha_composite(Image.new("RGBA", (OW, OH), (0, 0, 0, int(255 * (1 - f)))))
    return out.convert("RGB")

NF = int(DUR * FPS)
if __name__ == "__main__":
    if sys.argv[1] == "preview":
        for tt in sys.argv[2].split(","):
            frame(float(tt)).save(f"long/prev_{tt}.jpg", quality=85)
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"long/part{part}.mp4"], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 500 == 0: print(part, i, b, flush=True)
    p.stdin.close(); p.wait()
    print("part", part, "done", flush=True)
