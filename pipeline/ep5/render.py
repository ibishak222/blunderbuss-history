import math, os, subprocess, sys, glob, json
sys.path.insert(0, "ep5")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from plan import shots, chapters, DUR, TAGS, sent_time
import random

FPS, OW, OH = 24, 1920, 1080
L = "ep5/layers/"
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
CAM_OVERRIDE = {"cruise": ((1.0, 1200, 675), (1.04, 1200, 675)), "units": ((1.0, 1200, 675), (1.03, 1200, 690)), "trajectory": ((1.0, 1200, 675), (1.03, 1200, 690)),
                "arrival": ((1.0, 1200, 675), (1.08, 1250, 675)), "launch": ((1.0, 1200, 640), (1.06, 1250, 560))}
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

def sprite_at(out, name, x, y, scale, z, cx, cy, angle=0, alpha=1.0, anchor="c"):
    im = img(name)
    if angle: im = im.rotate(angle, resample=Image.BILINEAR, expand=True)
    sx, sy, k = to_screen(x, y, z, cx, cy)
    w, h = max(2, int(im.size[0] * k * scale)), max(2, int(im.size[1] * k * scale))
    paste_c(out, im.resize((w, h), Image.BILINEAR), sx, sy, alpha=alpha, anchor=anchor)

FD = mfont(36, b"Bold")
def ellipse_pt(cx0, cy0, rx, ry, a):
    return cx0 + rx * math.cos(a), cy0 + ry * math.sin(a)

def cruise(out, t, s, z, cx, cy):
    d = ImageDraw.Draw(out)
    lt = t - s["start"]; D = s["end"] - s["start"]
    S = lambda p: to_screen(p[0], p[1], z, cx, cy)[:2]
    # earth and mars positions; transfer arc from earth (angle pi) to mars (angle 0)
    q = ease(lt / D)
    ea = math.pi + q * 1.3; ma = -0.9 + q * 0.9
    e = S(ellipse_pt(1200, 675, 380, 300, ea)); m = S(ellipse_pt(1200, 675, 620, 470, ma))
    d.ellipse((e[0] - 16, e[1] - 16, e[0] + 16, e[1] + 16), fill=(80, 140, 220, 255))
    d.ellipse((m[0] - 14, m[1] - 14, m[0] + 14, m[1] + 14), fill=(200, 90, 50, 255))
    drift = "drifted" in " ".join(x["text"] for x in s["sents"])
    pts, pts2 = [], []
    for j in range(0, 61):
        f = j / 60 * q
        a = math.pi + f * math.pi
        rx = 380 + (620 - 380) * f; ry = 300 + (470 - 300) * f
        pts.append(S(ellipse_pt(1200, 675, rx, ry, a)))
        if drift: pts2.append(S(ellipse_pt(1200, 675, rx - 40 * f * f, ry - 30 * f * f, a)))
    if len(pts) > 1:
        d.line(pts, fill=(241, 228, 200, 220), width=4)
        if drift: d.line(pts2, fill=(217, 72, 43, 230), width=4)
        sp = pts2[-1] if drift else pts[-1]
        d.ellipse((sp[0] - 9, sp[1] - 9, sp[0] + 9, sp[1] + 9), fill=(255, 201, 74, 255))
    d.text(S((1200 - 380, 675 - 300 - 30)), "EARTH'S ORBIT", font=FD, fill=(80, 140, 220, 255), anchor="mm")
    d.text(S((1200 + 470, 675 - 470 - 10)), "MARS'S ORBIT", font=FD, fill=(200, 90, 50, 255), anchor="mm")
    if drift:
        d.text(S((1200, 1180)), "WHERE THEY THOUGHT IT WAS  ·  WHERE IT REALLY WAS", font=FD, fill=(241, 228, 200, 255), anchor="mm")

def units(out, t, s, z, cx, cy):
    d = ImageDraw.Draw(out)
    lt = t - s["start"]
    rr = random.Random(s["idx"])
    S = lambda p: to_screen(p[0], p[1], z, cx, cy)[:2]
    f = mfont(46, b"Bold")
    for j in range(7):
        tj = 1.0 + j * 1.6
        if lt < tj: break
        v = rr.uniform(0.2, 3.0)
        a = min(1, (lt - tj) / 0.4)
        y = 660 + j * 52
        d.text(S((700, y)), f"{v:.2f}  lbf·s", font=f, fill=(232, 200, 120, int(255 * a)), anchor="mm")
        d.text(S((1700, y)), f"read as {v:.2f} N·s", font=f, fill=(217, 90, 70, int(255 * a)), anchor="mm")
    if lt > 6:
        a = min(1, (lt - 6) / 0.6)
        d.text(S((1200, 1060)), "EVERY VALUE 4.45 TIMES TOO SMALL", font=mfont(52, b"ExtraBold"), fill=(255, 201, 74, int(255 * a)), anchor="mm")

ALT = [(226, (110, 200, 120), "PLANNED · 226 KM"), (80, (230, 150, 60), "LOWEST SURVIVABLE · ~80 KM"), (57, (217, 72, 43), "ACTUAL · ~57 KM")]
def trajectory(out, t, s, z, cx, cy):
    d = ImageDraw.Draw(out)
    lt = t - s["start"]
    S = lambda p: to_screen(p[0], p[1], z, cx, cy)[:2]
    R0, k_ = 2100, 2.6
    def arc(alt, col, width=5, dash=False, frac=1.0):
        rad = R0 + alt * k_
        pts = []
        for j in range(0, 81):
            a = math.radians(-90 - 30 + 60 * j / 80)
            if j / 80 > frac: break
            pts.append(S((1200 + rad * math.cos(a), 3100 + rad * math.sin(a))))
        if len(pts) > 1:
            if dash:
                for i in range(0, len(pts) - 1, 2): d.line([pts[i], pts[i + 1]], fill=col, width=width)
            else: d.line(pts, fill=col, width=width)
    txt = " ".join(x["text"] for x in s["sents"])
    show_actual = "fifty-seven" in txt
    for alt, col, lab in ALT:
        if alt == 57 and not show_actual: continue
        arc(alt, col + (220,), 5, dash=(alt != 57))
        p = S((1200 + (R0 + alt * k_) * math.cos(math.radians(-122)), 3100 + (R0 + alt * k_) * math.sin(math.radians(-122)) - 10))
        d.text((p[0] - 10, p[1]), lab, font=mfont(30, b"Bold"), fill=col + (255,), anchor="rb")
    # estimate marker dropping through the week
    if "kept dropping" in txt:
        steps = [(sent_time(s, "kept dropping"), 226), (sent_time(s, "One hundred and seventy"), 170), (sent_time(s, "One hundred and fifty"), 150),
                 (sent_time(s, "Twenty-four hours"), 110)]
        cur = 226
        for (ts, v) in steps:
            if ts and t >= ts: cur = v
        x, y = S((1200, 3100 - (R0 + cur * k_)))
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(255, 201, 74, 255))
        d.text((x + 30, y), f"ESTIMATE: {cur} KM", font=mfont(40, b"ExtraBold"), fill=(255, 201, 74, 255), anchor="lm")
    if show_actual:
        q = ease(lt / 6)
        pts = []
        for j in range(0, 41):
            f = j / 40 * q
            a = math.radians(-125 + 70 * f)
            alt = 57 + (320 - 57) * (1 - math.sin(math.pi * f))
            pts.append(S((1200 + (R0 + alt * k_) * math.cos(a), 3100 + (R0 + alt * k_) * math.sin(a))))
        if len(pts) > 1: d.line(pts, fill=(255, 255, 255, 230), width=4)

def control_fx(out, t, z, cx, cy):
    ov = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    rr = random.Random(int(t * 3))
    for i, x in enumerate(range(260, 2300, 420)):
        if rr.random() < 0.5:
            sx, sy = to_screen(x + 12, 532, z, cx, cy)[:2]; ex, ey = to_screen(x + 288, 708, z, cx, cy)[:2]
            d.rectangle((sx, sy, ex, ey), fill=(122, 240, 168, 28))
    out.alpha_composite(ov)

def layered(out, t, s):
    k = s["shot"]
    lt = t - s["start"]
    z, cx, cy = camera(s, t)
    place(img(k + "_back"), z, cx, cy, out)
    if k == "arrival":
        txt = " ".join(x["text"] for x in s["sents"])
        behind = sent_time(s, "passed behind") or sent_time(s, "waited for it to reappear") or 1e9
        burn = sent_time(s, "insertion burn") or sent_time(s, "fired its engine") or s["start"] + 1
        p = ease((t - s["start"]) / max(2, behind - s["start"]))
        ox, oy = 500 + (1300 - 500) * p, 420 + (560 - 420) * p
        hidden = t > behind
        if not hidden:
            if t > burn: sprite_at(out, "flame", ox - 30, oy + 140, 0.6, z, cx, cy, angle=-20, alpha=0.9)
            sprite_at(out, "orbiter", ox, oy, 0.55, z, cx, cy, angle=-20)
        place(img("arrival_planet"), z, cx, cy, out)
    elif k == "mars":
        a = lt * 0.05
        ox, oy = 1500 + 760 * math.cos(a + 3.6), 700 + 260 * math.sin(a + 3.6)
        sprite_at(out, "orbiter", ox, oy, 0.4, z, cx, cy, angle=10)
    elif k == "orbiter":
        pass
    elif k == "cruise":
        cruise(out, t, s, z, cx, cy)
    elif k == "units":
        units(out, t, s, z, cx, cy)
    elif k == "trajectory":
        trajectory(out, t, s, z, cx, cy)
    elif k == "launch":
        lift = sent_time(s, "launched") or s["start"] + 2
        q = max(0.0, t - lift - 0.8)
        ry = 980 - 0.5 * 60 * q * q
        if t > lift:
            for j in range(8):
                sprite_at(out, "plume", 1230 + (j - 4) * 90 * min(1, q + 0.3), 980 - j % 3 * 40, 0.9 + 0.3 * min(q, 2), z, cx, cy, alpha=0.8)
            sprite_at(out, "flame", 1230, ry + 120, 0.9, z, cx, cy, angle=180)
        sprite_at(out, "rocket", 1230, ry, 1.0, z, cx, cy, anchor="b")
    place(img(k + "_front"), z, cx, cy, out)
    if k == "control":
        control_fx(out, t, z, cx, cy)

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

def title_scene(out, t, s):
    place(img("mars_back"), 1.05, 1200, 675, out)
    out.alpha_composite(Image.new("RGBA", (OW, OH), (6, 8, 16, 150)))
    lt = t - s["start"]; k = ease(lt / 1.0)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 440), "MARS CLIMATE ORBITER", font=ImageFont.truetype(FSC, 126), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 570), "Lost in space by a units mix-up, 1999", font=pfont(48, b"Bold"), fill=(255, 201, 74, int(255 * k)), anchor="mm")
    d.line((760, 630, 1160, 630), fill=(217, 72, 43, int(255 * k)), width=4)

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
REPL = [("nineteen ninety-nine", "1999"), ("nineteen ninety-eight", "1998"), ("nineteen ninety-seven", "1997"), ("nineteen ninety-three", "1993"),
        ("nineteen nineties", "1990s"), ("six hundred and sixty-nine million", "669 million"), ("six hundred and thirty-eight", "638"),
        ("three hundred and twenty-seven million dollars", "$327 million"), ("three hundred million dollar", "$300 million"),
        ("four point four five", "4.45"), ("two hundred and twenty-six", "226"), ("One hundred and seventy", "170"), ("One hundred and fifty", "150"),
        ("a hundred and ten", "110"), ("fifty-seven", "57"), ("thirty percent", "30%"), ("Twenty-four hours", "24 hours"), ("forty-nine", "49"),
        ("eighty.", "80."), ("ninety-eight", "'98"), ("twenty-third of September", "23rd of September"), ("eleventh of December", "11th of December"),
        ("Delta Two", "Delta II")]
_tim = json.load(open("ep5/timing.json"))
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

LAYERED = {"arrival", "control", "mars", "orbiter", "launch", "cruise", "units", "trajectory"}
def frame(t):
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[0] if t < shots[0]["start"] else shots[-1])
    k = s["shot"]
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    random.seed(int(t * FPS))
    if k in LAYERED: layered(out, t, s)
    elif k == "paper": paper_scene(out, t, s, "paper", None)
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
            frame(float(tt)).save(f"ep5/prev_{tt}.jpg", quality=85)
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"ep5/part{part}.mp4"], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 500 == 0: print(part, i, b, flush=True)
    p.stdin.close(); p.wait()
    print("part", part, "done", flush=True)
