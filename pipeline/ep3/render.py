import math, os, subprocess, sys, glob, json
sys.path.insert(0, "ep3")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from plan import shots, chapters, DUR, TAGS, sent_time, GUSTS, SALUTE
import random

FPS, OW, OH = 24, 1920, 1080
L = "ep3/layers/"
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
CAM_OVERRIDE = {"sinking": ((1.05, 1200, 715), (1.1, 1200, 735)), "test": ((1.05, 1200, 640), (1.12, 1200, 620)),
                "raising": ((1.0, 1200, 680), (1.05, 1200, 660)), "harbour_sail": ((1.06, 1250, 720), (1.12, 1150, 740))}
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

def gust_heel(t):
    h = 3 + 1.5 * math.sin(t * 0.9)
    for (gt, st) in GUSTS:
        dt = t - gt
        if 0 <= dt < 7:
            h += st * (ease(dt / 1.2) if dt < 2.5 else 1 - ease((dt - 2.5) / 3.5))
    return h

def draw_ship(out, sprite, x, y, scale, heel, z, cx, cy, crop_below=None):
    """sprite waterline anchor at (560, 840); heel in degrees (positive = leans to port/left)"""
    im = img(sprite)
    rot = im.rotate(heel, resample=Image.BILINEAR, center=(560, 840))
    sx, sy, k = to_screen(x, y, z, cx, cy)
    kk = k * scale
    rs = rot.resize((max(2, int(1120 * kk)), max(2, int(960 * kk))), Image.BILINEAR)
    _paste_clip(out, rs, int(sx - 560 * kk), int(sy - 840 * kk))

def smoke_puffs(out, t, t0, x, y, scale, z, cx, cy):
    for j in range(12):
        ti = t0 + j * 0.18
        if 0 <= t - ti < 3.0:
            q = (t - ti) / 3.0
            px = x + (-230 + j * 40) * scale
            py = y - 100 * scale - q * 120 * scale
            sx, sy, k = to_screen(px + q * 60, py, z, cx, cy)
            sz = int(300 * k * scale * (0.35 + q * 0.9))
            paste_c(out, img("smoke").resize((max(2, sz), max(2, sz))), sx, sy, alpha=0.85 * (1 - q))

def rain(out, t, n=220, col=(190, 200, 210, 80)):
    d = ImageDraw.Draw(out)
    r = random.Random(int(t * 24))
    for _ in range(n):
        x, y = r.randint(-100, OW), r.randint(-50, OH)
        d.line((x, y, x + 14, y + 50), fill=col, width=2)

def layered(out, t, s):
    k = s["shot"]
    z, cx, cy = camera(s, t)
    lt = t - s["start"]
    back = {"harbour_sail": "harbour_back", "sinking": "sinking_back"}.get(k, k + "_back")
    place(img(back), z, cx, cy, out)
    if k == "harbour_sail":
        D = s["end"] - s["start"]
        x = 1750 - 700 * (lt / D) if s["idx"] > 0 else 1500 - 300 * (lt / D)
        draw_ship(out, "vasa", x, 965, 0.85, gust_heel(t), z, cx, cy)
        for st in SALUTE:
            smoke_puffs(out, t, st + 1.0, x, 965, 0.85, z, cx, cy)
        place(img("harbour_front"), z, cx, cy, out)
    elif k == "sinking":
        g = [gt for (gt, st) in GUSTS if s["start"] <= gt < s["end"]]
        gt = g[0] if g else s["start"] + 2
        st_ = sent_time(s, "the vasa sank") or sent_time(s, "the vasa sank.") or (gt + 3.5)
        heel = 4 + 30 * ease((t - gt) / 2.5)
        sink = ease((t - st_ - 0.4) / 6.0)
        y = 965 + sink * 500
        draw_ship(out, "vasa", 1200, y, 0.85, heel - 8 * sink, z, cx, cy)
        # water covers the hull as it goes down
        place(img("harbour_front"), z, cx, cy, out)
        if sink > 0.8:
            d = ImageDraw.Draw(out)
            rr = random.Random(5)
            for j in range(16):
                px, py = 900 + rr.uniform(0, 600), 975 + rr.uniform(-5, 25)
                sx, sy, kk = to_screen(px + math.sin(t + j) * 8, py, z, cx, cy)
                d.ellipse((sx - 5 * kk * 2, sy - 5 * kk * 2, sx + 5 * kk * 2, sy + 5 * kk * 2), fill=(20, 16, 14, 230))
    elif k == "test":
        runs = sent_time(s, "After three runs") or (s["start"] + 8)
        start = sent_time(s, "Thirty men were told") or (s["start"] + 4)
        amp = 2 + 16 * ease((t - start) / 6) * (1 - ease((t - runs - 2.5) / 2.0))
        ang = amp * math.sin((t - start) * 1.6)
        im = img("stern").rotate(ang, resample=Image.BILINEAR, center=(250, 820))
        sx, sy, kk = to_screen(1200, 1000, z, cx, cy)
        kk *= 1.15
        rs = im.resize((int(500 * kk), int(900 * kk)), Image.BILINEAR)
        _paste_clip(out, rs, int(sx - 250 * kk), int(sy - 820 * kk))
        # thirty men running across the upper deck (y = -222 in hull coords), side follows the roll
        if amp > 3:
            d = ImageDraw.Draw(out)
            side = math.cos((t - start) * 1.6)
            a = math.radians(-ang)
            for j in range(30):
                lx = side * 90 + ((j % 10) - 4.5) * 9 + (j // 10) * 3
                ly = -222
                rx = lx * math.cos(a) - ly * math.sin(a)
                ry = lx * math.sin(a) + ly * math.cos(a)
                px, py = sx + rx * kk, sy + ry * kk
                d.rectangle((px - 2.5 * kk, py - 18 * kk, px + 2.5 * kk, py), fill=(20, 14, 12, 255))
        place(img("test_front"), z, cx, cy, out)
    elif k == "underwater":
        place(img("underwater_front"), z, cx, cy, out)
        rr = random.Random(3)
        for j in range(26):
            bx = rr.uniform(700, 1800); speed = rr.uniform(60, 140); ph = rr.uniform(0, 20)
            by = 1050 - ((lt * speed + ph * 50) % 1050)
            sx, sy, kk = to_screen(bx + math.sin(lt * 2 + j) * 12, by, z, cx, cy)
            paste_c(out, img("bubble").resize((max(2, int(40 * kk * rr.uniform(0.5, 1.2))),) * 2), sx, sy, alpha=0.8)
        for j in range(3):
            fx = (lt * (60 + j * 25) + j * 700) % 2800 - 200
            sx, sy, kk = to_screen(fx, 500 + j * 150, z, cx, cy)
            paste_c(out, img("fish").resize((int(130 * kk), int(60 * kk))), sx, sy, alpha=0.7)
    elif k == "raising":
        idxs = [x["idx"] for x in shots if x["shot"] == "raising"]
        first = s["idx"] == idxs[0]
        D = s["end"] - s["start"]
        surf = sent_time(s, "broke the surface")
        if first:
            y = 1250 - 250 * ease(lt / D)
            if surf: y = 1250 - 250 * ease((t - s["start"]) / max(1, surf - s["start"])) - 440 * ease((t - surf) / 5)
        else:
            y = 560
        draw_ship(out, "hull_rise", 1200, y, 1.0, 0, z, cx, cy)
        d = ImageDraw.Draw(out)
        for px, hx in ((660, 900), (1740, 1500)):
            a = to_screen(px, 440, z, cx, cy); b = to_screen(hx, y - 120, z, cx, cy)
            d.line((a[0], a[1], b[0], b[1]), fill=(30, 30, 30, 230), width=4)
        place(img("raising_front"), z, cx, cy, out)
    else:
        place(img(k + "_front"), z, cx, cy, out)
        if k == "navy":
            rain(out, t, 300)
            if int(t * 10) % 97 == 0:
                out.alpha_composite(Image.new("RGBA", (OW, OH), (230, 235, 255, 90)))

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
    place(img("harbour_back"), 1.05, 1200, 700, out)
    draw_ship(out, "vasa", 1250, 965, 0.85, 3 + 1.5 * math.sin(t), 1.05, 1200, 700)
    place(img("harbour_front"), 1.05, 1200, 700, out)
    out.alpha_composite(Image.new("RGBA", (OW, OH), (10, 14, 22, 150)))
    lt = t - s["start"]; k = ease(lt / 1.0)
    d = ImageDraw.Draw(out)
    d.text((OW / 2, 450), "THE VASA", font=ImageFont.truetype(FSC, 170), fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW / 2, 580), "Sweden's mightiest warship, 1628", font=pfont(48, b"Bold"), fill=(255, 201, 74, int(255 * k)), anchor="mm")
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
REPL = [("eighteen forty-four", "1844"), ("eighteen nineties", "1890s"), ("nineteen twenty,", "1920,"), ("sixteen twenty-eight", "1628"), ("sixteen twenty-seven", "1627"), ("sixteen twenty-six", "1626"), ("sixteen twenty-five", "1625"),
        ("sixteen twenty-one", "1621"), ("sixteen sixties", "1660s"), ("sixteen hundreds", "1600s"), ("nineteen fifty-six", "1956"),
        ("nineteen fifty-nine", "1959"), ("nineteen sixty-one", "1961"), ("nineteen fifties", "1950s"), ("nineteen ninety", "1990"),
        ("three hundred and thirty-three", "333"), ("thirteen hundred", "1,300"), ("a hundred and twenty", "120"), ("thirty-two", "32"),
        ("seventy-two", "72"), ("twenty-four-pound", "24-pound"), ("forty-three", "43"), ("forty-five million", "45 million"),
        ("twelve hundred", "1,200"), ("one hundred and forty-five", "145"), ("three hundred", "300"), ("sixty-nine", "69"),
        ("five hundred", "500"), ("seventeen years", "17 years"), ("tenth of August", "10th of August"), ("sixteenth of January", "16th of January"),
        ("twenty-fourth of April", "24th of April")]
_tim = json.load(open("ep3/timing.json"))
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

LAYERED = {"harbour_sail", "sinking", "king", "navy", "shipyard", "plans", "carvings", "test", "underwater", "raising", "museum"}
def frame(t):
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[0] if t < shots[0]["start"] else shots[-1])
    k = s["shot"]
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    random.seed(int(t * FPS))
    if k in LAYERED: layered(out, t, s)
    elif k == "inquiry": paper_scene(out, t, s, "inquiry", None)
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
            frame(float(tt)).save(f"ep3/prev_{tt}.jpg", quality=85)
        sys.exit()
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", f"ep3/part{part}.mp4"], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 500 == 0: print(part, i, b, flush=True)
    p.stdin.close(); p.wait()
    print("part", part, "done", flush=True)
