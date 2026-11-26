import math, os, subprocess, sys, glob, json
sys.path.insert(0, "ep4")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from plan import shots, chapters, DUR, TAGS, sent_time
import random

FPS, OW, OH = 24, 1920, 1080
L = "ep4/layers/"
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
CAM_OVERRIDE = {"diagram_a": ((1.0, 1200, 675), (1.0, 1200, 675)), "diagram_b": ((1.0, 1200, 675), (1.0, 1200, 675)),
                "collision": ((1.05, 1250, 760), (1.12, 1300, 740)), "sinking": ((1.05, 1200, 730), (1.12, 1150, 740)), "wreck": ((1.0, 1200, 700), (1.12, 1200, 560))}
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

def draw_ship(out, sprite, x, y, scale, angle, z, cx, cy, sqx=1.0, flip=False):
    """sprite 1000x760, waterline anchor (500, 600); angle in degrees (PIL rotate, + = counter-clockwise)"""
    im = img(sprite)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    rot = im.rotate(angle, resample=Image.BILINEAR, center=(500, 600))
    sx, sy, k = to_screen(x, y, z, cx, cy)
    kx, ky = k * scale * sqx, k * scale
    rs = rot.resize((max(2, int(1000 * kx)), max(2, int(760 * ky))), Image.BILINEAR)
    _paste_clip(out, rs, int(sx - 500 * kx), int(sy - 600 * ky))

def flash_at(out, x, y, size, z, cx, cy, alpha=1.0):
    sx, sy, k = to_screen(x, y, z, cx, cy)
    g = max(2, int(300 * k * size))
    paste_c(out, img("flash").resize((g, g)), sx, sy, alpha=alpha)

def splash_at(out, x, y, size, q, z, cx, cy):
    sx, sy, k = to_screen(x, y, z, cx, cy)
    h = int(330 * k * size * (0.3 + 0.9 * math.sin(min(1, q * 1.4) * math.pi / 2))); w = int(300 * k * size * 0.8)
    if h > 2 and w > 2: paste_c(out, img("splash").resize((w, h)), sx, sy, alpha=max(0, 1 - q), anchor="b")

def men_in_water(out, t, z, cx, cy, n=24, x0=900, x1=1700, y=1030):
    rr = random.Random(7)
    for j in range(n):
        px = rr.uniform(x0, x1) + math.sin(t * 0.8 + j) * 10
        py = y + rr.uniform(-6, 26) + math.sin(t * 1.7 + j) * 4
        sx, sy, k = to_screen(px, py, z, cx, cy)
        m = img("man").resize((max(2, int(26 * k * 1.4)), max(2, int(30 * k * 1.4))))
        paste_c(out, m, sx, sy)

# plan-view diagram
CH = (42, 74, 86, 255)
def ship_icon(d, x, y, heading, col, size=1.0):
    """heading in degrees, 0 = up (north), clockwise positive; screen coords"""
    pts = [(0, -38), (12, -10), (12, 30), (-12, 30), (-12, -10)]
    a = math.radians(heading)
    P = [(x + px * size * math.cos(a) - py * size * math.sin(a), y + px * size * math.sin(a) + py * size * math.cos(a)) for px, py in pts]
    d.polygon(P, fill=col, outline=(20, 20, 24, 255))

def turn_pos(cx0, cy0, r, ang, direction):
    """ship starting at (cx0 + -direction*r ... ) heading north, turning towards +direction (1 = right/east, -1 = left/west).
    ang = degrees turned so far. returns x, y, heading"""
    a = math.radians(ang)
    centre_x = cx0 + direction * r
    x = centre_x - direction * r * math.cos(a)
    y = cy0 - r * math.sin(a)
    return x, y, direction * ang

FD = mfont(34, b"Bold")
def diagram(out, t, s):
    out.alpha_composite(img("chart").resize((OW, OH)))
    d = ImageDraw.Draw(out)
    lt = t - s["start"]
    S = 0.8
    xa, xb = 960 * S / 0.8 * 0.8, 1560 * S / 0.8 * 0.8  # canvas -> screen (BASE 0.8)
    xa, xb = 960 * S, 1560 * S
    gap = xb - xa
    victoria_col, camper_col, other = (217, 72, 43, 255), (43, 93, 168, 255), (60, 70, 80, 255)
    if s["shot"] == "diagram_a":
        y0 = 470 - lt * 3
        for j in range(6):
            ship_icon(d, xa, y0 + j * 95, 0, victoria_col if j == 0 else other)
        for j in range(5):
            ship_icon(d, xb, y0 + j * 95, 0, camper_col if j == 0 else other)
        d.text((xa - 30, y0 - 70), "VICTORIA", font=FD, fill=victoria_col, anchor="rm")
        d.text((xb + 30, y0 - 70), "CAMPERDOWN", font=FD, fill=camper_col, anchor="lm")
        yy = y0 + 200
        d.line((xa, yy, xb, yy), fill=CH, width=4)
        for xx in (xa, xb): d.line((xx, yy - 16, xx, yy + 16), fill=CH, width=4)
        d.text(((xa + xb) / 2, yy + 34), "6 CABLES · 1,200 YARDS", font=FD, fill=CH, anchor="mm")
        tc = sent_time(s, "turning circle")
        if tc and t > tc:
            k = ease((t - tc) / 1.2)
            r = gap * (800 / 1200) / 2
            for (x, sgn, col) in ((xa, 1, victoria_col), (xb, -1, camper_col)):
                ccx = x + sgn * r
                for a0 in range(0, 360, 12):
                    if a0 / 360 > k: break
                    a1 = math.radians(a0); a2 = math.radians(a0 + 6)
                    d.line((ccx + r * math.cos(a1), y0 + r * math.sin(a1), ccx + r * math.cos(a2), y0 + r * math.sin(a2)), fill=col, width=4)
            d.text(((xa + xb) / 2, y0 - 300), "EACH TURNING CIRCLE ≈ 800 YARDS ACROSS", font=FD, fill=(20, 30, 36, int(255 * k)), anchor="mm")
            d.text(((xa + xb) / 2, y0 - 255), "SAFE GAP NEEDED ≈ 1,600 YARDS", font=FD, fill=(217, 72, 43, int(255 * k)), anchor="mm")
    else:
        y0 = 560
        D = s["end"] - s["start"]
        T_hit = 7.5
        r = gap * (800 / 1200) / 2
        p = min(lt, T_hit)
        ang_v = min(150, p / T_hit * 118)
        ang_c = min(150, p / T_hit * 100)
        trail_v, trail_c = [], []
        for q in range(0, 41):
            a_ = ang_v * q / 40; trail_v.append(turn_pos(xa, y0, r, a_, 1)[:2])
            a_ = ang_c * q / 40; trail_c.append(turn_pos(xb, y0, r * 1.25, a_, -1)[:2])
        d.line(trail_v, fill=(217, 72, 43, 160), width=3); d.line(trail_c, fill=(43, 93, 168, 160), width=3)
        for j in range(1, 6):
            ship_icon(d, xa, y0 + j * 95 - p * 8, 0, other)
        for j in range(1, 5):
            ship_icon(d, xb, y0 + j * 95 - p * 8, 0, other)
        xv, yv, hv = turn_pos(xa, y0, r, ang_v, 1)
        xc, yc, hc = turn_pos(xb, y0, r * 1.25, ang_c, -1)
        ship_icon(d, xv, yv, hv, (217, 72, 43, 255), 1.2); ship_icon(d, xc, yc, hc, (43, 93, 168, 255), 1.2)
        if lt >= T_hit:
            q = min(1, (lt - T_hit) / 0.4)
            rr = 40 + 60 * q
            d.ellipse(((xv + xc) / 2 - rr, (yv + yc) / 2 - rr, (xv + xc) / 2 + rr, (yv + yc) / 2 + rr), outline=(217, 72, 43, int(255 * (1 - q * 0.5))), width=6)
            d.text(((xv + xc) / 2, (yv + yc) / 2 - 150), "COLLISION", font=mfont(52, b"ExtraBold"), fill=(217, 72, 43, 255), anchor="mm")

def layered(out, t, s):
    k = s["shot"]
    lt = t - s["start"]
    if k in ("diagram_a", "diagram_b"):
        diagram(out, t, s); return
    z, cx, cy = camera(s, t)
    back = {"collision": "sea_back", "sinking": "sea_back"}.get(k, k + "_back")
    front = {"collision": "sea_front", "sinking": "sea_front"}.get(k, k + "_front")
    place(img(back), z, cx, cy, out)
    if k == "collision":
        hit = sent_time(s, "It struck") or sent_time(s, "rammed") or (s["start"] + 3.5)
        if s["idx"] == 1: hit = s["start"] + 3.2
        back_off = sent_time(s, "backed away") or (hit + 6)
        shake = 0
        if hit <= t < hit + 0.6:
            shake = 10 * (1 - (t - hit) / 0.6) * math.sin(t * 80)
        cxx, cyy = cx + shake, cy + shake * 0.5
        vb = -2.5 * ease((t - hit - 1.0) / 6)
        draw_ship(out, "victoria", 1050, 1015, 1.0, vb, z, cxx, cyy)
        approach = ease((t - (hit - 4.0)) / 4.0)
        retreat = ease((t - back_off) / 4.0)
        cxp = 2700 - (2700 - 1700) * approach + 260 * retreat
        draw_ship(out, "camperdown", cxp, 1045, 1.15, -2, z, cxx, cyy, sqx=0.55, flip=True)
        if t >= hit:
            if t - hit < 0.35: flash_at(out, 1480, 990, 1.4, z, cxx, cyy)
            if t - hit < 1.4: splash_at(out, 1480, 1030, 1.4, (t - hit) / 1.4, z, cxx, cyy)
        place(img(front), z, cxx, cyy, out)
        if hit <= t < hit + 0.15:
            out.alpha_composite(Image.new("RGBA", (OW, OH), (255, 240, 220, 90)))
    elif k == "sinking":
        plunge = sent_time(s, "rolled over and plunged") or (s["start"] + 20)
        a = -3 - 14 * ease(lt / max(4, plunge - s["start"]))
        sink = 120 * ease(lt / max(4, plunge - s["start"]))
        if t > plunge:
            q = ease((t - plunge) / 6)
            a += -30 * q; sink += 700 * q
        draw_ship(out, "victoria", 1150, 1015 + sink, 1.05, a, z, cx, cy)
        place(img(front), z, cx, cy, out)
        if t > plunge - 6:
            men_in_water(out, t, z, cx, cy)
    elif k == "signals":
        place(img(front), z, cx, cy, out)
        for j in range(4):
            t0 = s["start"] + 0.8 + j * 0.7
            q = ease((t - t0) / 1.4)
            if q <= 0: continue
            side = -1 if j % 2 == 0 else 1
            fx = 1097 + side * (260 + (j // 2) * 170)
            fy = 1350 - (1350 - (300 + (j // 2) * 10)) * q
            sx, sy, kk = to_screen(fx, fy, z, cx, cy)
            fl = img(f"flag{j}")
            wob = math.sin(t * 6 + j) * 3
            fl2 = fl.resize((int(150 * kk), int(120 * kk))).rotate(wob, expand=True, resample=Image.BILINEAR)
            paste_c(out, fl2, sx, sy, anchor="c")
    elif k == "ghost":
        place(img(front), z, cx, cy, out)
        gt = sent_time(s, "walk silently") or (s["start"] + 6)
        if gt - 0.5 < t < gt + 7:
            q = (t - gt + 0.5) / 7.5
            gx = 700 + 900 * q
            alpha = 0.45 * math.sin(math.pi * min(1, max(0, q)))
            sx, sy, kk = to_screen(gx, 1110, z, cx, cy)
            gh = img("ghost").resize((int(300 * kk * 1.1), int(440 * kk * 1.1)))
            paste_c(out, gh, sx, sy, alpha=alpha, anchor="b")
    else:
        place(img(front), z, cx, cy, out)

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
    place(img("fleet_back"), 1.05, 1200, 700, out); place(img("fleet_front"), 1.05, 1200, 700, out)
    out.alpha_composite(Image.new("RGBA", (OW, OH), (10, 14, 22, 150)))
    lt = t - s["start"]; k = ease(lt / 1.0)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 450), "HMS VICTORIA", font=ImageFont.truetype(FSC, 160), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 580), "The day the Royal Navy sank its own flagship, 1893", font=pfont(46, b"Bold"), fill=(255, 201, 74, int(255 * k)), anchor="mm")
    d.line((760, 640, 1160, 640), fill=(217, 72, 43, int(255 * k)), width=4)

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
REPL = [("eighteen ninety-three", "1893"), ("eighteen ninety-two", "1892"), ("eighteen nineties", "1890s"), ("eighteen sixty-six", "1866"),
        ("nineteen sixteen", "1916"), ("two thousand and four", "2004"), ("three hundred and fifty-eight", "358"),
        ("sixteen-and-a-quarter-inch", "16.25-inch"), ("twelve hundred", "1,200"), ("eight hundred", "800"), ("sixteen hundred", "1,600"),
        ("a hundred and forty", "140"), ("thirty metres", "30 metres"), ("twenty-second of June", "22nd of June"),
        ("twenty-second of August", "22nd of August"), ("three thirty", "3:30"), ("sixteen points", "16 points")]
_tim = json.load(open("ep4/timing.json"))
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

LAYERED = {"fleet", "victoria", "tryon", "bridge", "signals", "diagram_a", "diagram_b", "collision", "sinking", "rescue", "ghost", "jellicoe", "wreck"}
def frame(t):
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[0] if t < shots[0]["start"] else shots[-1])
    k = s["shot"]
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    random.seed(int(t * FPS))
    if k in LAYERED: layered(out, t, s)
    elif k in ("court", "paper"): paper_scene(out, t, s, k, None)
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
            frame(float(tt)).save(f"ep4/prev_{tt}.jpg", quality=85)
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"ep4/part{part}.mp4"], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 500 == 0: print(part, i, b, flush=True)
    p.stdin.close(); p.wait()
    print("part", part, "done", flush=True)
