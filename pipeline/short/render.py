import json, math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS, OW, OH = 30, 1080, 1920
L = "video/layers/"
timing = json.load(open("timing.json"))
DUR = timing[-1]["end"] + 0.9
NF = int(DUR * FPS)

def load(n):
    return Image.open(L + n + ".png").convert("RGBA")

LY = {n: load(n) for n in ["s1_sky", "s1_ships", "s1_fog", "s1_sea", "s2_sky", "s2_sea", "s2_trawlers_far",
                           "s2_crane", "s2_fg", "beam", "flash", "splash", "s3_desk", "s3_paper", "stamp",
                           "s4_sky", "s4_ships", "s4_sea"]}
LOGO = Image.open("brand/logo_icon.png").convert("RGBA").resize((560, 560), Image.LANCZOS)
mask = Image.new("L", (560, 560), 0); ImageDraw.Draw(mask).ellipse((0, 0, 559, 559), fill=255)
LOGO.putalpha(mask)

T = [x["start"] for x in timing]
CUT2, CUT3, CUT4, CUTEND = T[3] - 0.15, T[7] - 0.15, T[8] - 0.12, T[9] - 0.12
FIRE = T[4] + 1.0  # "Guns firing"

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def place(layer, z, cx, cy, out, base=0.8):
    """Draw a layer (1350x2400 canvas coords) into out with zoom z centred on (cx,cy)."""
    s = base * z
    a = 1.0 / s
    data = (a, 0, cx - (OW / 2) * a, 0, a, cy - (OH / 2) * a)
    im = layer.transform((OW, OH), Image.AFFINE, data, resample=Image.BILINEAR)
    out.alpha_composite(im)

def cam(t, t0, t1, z0, z1, c0, c1):
    p = ease((t - t0) / (t1 - t0))
    return z0 + (z1 - z0) * p, c0[0] + (c1[0] - c0[0]) * p, c0[1] + (c1[1] - c0[1]) * p

def shake(t, start, amp=10, length=99):
    if t < start or t > start + length: return 0, 0
    k = amp * math.exp(-((t - start) % 0.55) * 5)
    return k * math.sin(t * 91), k * math.cos(t * 77)

random.seed(2)
SHOTS = sorted(FIRE + random.uniform(0, 7.5) for _ in range(16))
SPLASH = [(FIRE + 0.4 + i * 0.9, random.choice([300, 520, 760, 980, 1150]), random.choice([1300, 1340, 1380])) for i in range(8)]

def scene1(t, out):
    z, cx, cy = cam(t, 0, CUT2, 1.0, 1.22, (675, 1200), (720, 1330))
    for n, d in [("s1_sky", 1.0), ("s1_ships", 1.0), ("s1_sea", 1.0), ("s1_fog", 1.15)]:
        zl = 1 + (z - 1) * d
        drift = (t * 6) if n != "s1_fog" else t * 18
        place(LY[n], zl, cx - drift, cy, out)

def scene2(t, out):
    lt = t - CUT2
    z, cx, cy = cam(t, CUT2, CUT3, 1.05, 1.32, (675, 1250), (760, 1420))
    sx, sy = shake(t, FIRE, 9)
    cx += sx; cy += sy
    dyn = Image.new("RGBA", (1350, 2400), (0, 0, 0, 0))
    # searchlights: exact affine from each ship's lamp (s2_sky ships at waterline 1254)
    if t > T[4] - 0.1:
        on = ease((t - (T[4] - 0.1)) / 0.25)
        for i, (ox, oy, base, sp) in enumerate([(15, 1143, 4, 0.6), (284, 1174, 3, 0.45), (460, 1194, 2, 0.7)]):
            th = math.radians(base + 4 * math.sin(lt * sp + i))
            c, sn = math.cos(th), math.sin(th)
            data = (c, sn, -(c * ox + sn * oy), -sn, c, (sn * ox - c * oy) + 200)
            b = LY["beam"].transform((1350, 2400), Image.AFFINE, data, resample=Image.BILINEAR)
            if on < 1:
                b.putalpha(b.getchannel("A").point(lambda v: int(v * on)))
            dyn.alpha_composite(b)
            g = LY["flash"].resize((60, 60))
            dyn.alpha_composite(g, (ox - 30, oy - 30))
    # far trawlers
    dyn.alpha_composite(LY["s2_trawlers_far"], (0, 0))
    # the Crane: bobs, then lists and sinks
    crane = LY["s2_crane"]
    sink_t = ease((t - (T[6] + 0.4)) / 4.2)
    ang = 2.0 * math.sin(lt * 1.6) + 24 * sink_t
    rc = crane.rotate(ang, resample=Image.BILINEAR, center=(380, 430))
    sink = int(sink_t * 210 + 6 * math.sin(lt * 1.3))
    cut = max(1, 430 + 12 - sink)
    rc = rc.crop((0, 0, 760, cut))
    dyn.alpha_composite(rc, (420, 1330 - 430 + sink))
    # muzzle flashes on the horizon + splashes near the boats
    for s in SHOTS:
        if s <= t < s + 0.22:
            k = 1 - (t - s) / 0.22
            fx, fy = [(47, 1223), (307, 1232), (478, 1237)][int(s * 10) % 3]
            f = LY["flash"].resize((int(160 * (0.6 + k)), int(160 * (0.6 + k))))
            dyn.alpha_composite(f, (fx - f.size[0] // 2, fy - f.size[1] // 2))
    for (s, x, y) in SPLASH:
        if s <= t < s + 0.9:
            k = (t - s) / 0.9
            h = int(330 * (0.3 + 0.9 * math.sin(min(1, k * 1.4) * math.pi / 2)))
            sp = LY["splash"].resize((int(300 * 0.7), max(2, int(h * 0.7))))
            a = sp.getchannel("A").point(lambda v: int(v * (1 - k))); sp.putalpha(a)
            dyn.alpha_composite(sp, (x - sp.size[0] // 2, y - sp.size[1]))
    for n, d in [("s2_sky", 0.9), ("s2_sea", 0.9), ("DYN", 0.9), ("s2_fg", 1.25)]:
        zl = 1 + (z - 1) * d
        place(dyn if n == "DYN" else LY[n], zl, cx, cy, out)
    # flash light on whole frame when guns fire
    for s in SHOTS:
        if s <= t < s + 0.12:
            ov = Image.new("RGBA", (OW, OH), (255, 200, 140, int(70 * (1 - (t - s) / 0.12))))
            out.alpha_composite(ov)

def scene3(t, out):
    lt = t - CUT3
    out.alpha_composite(LY["s3_desk"].resize((OW, OH)))
    z = 0.92 + 0.12 * ease(lt / 4.6)
    sx, sy = shake(t, CUT3 + 0.05, 14, 0.5)
    pw, ph = int(1150 * 0.8 * z), int(1650 * 0.8 * z)
    p = LY["s3_paper"].resize((pw, ph), Image.BILINEAR).rotate(-2 + 2 * ease(lt / 1.2), resample=Image.BILINEAR, expand=True)
    sh = Image.new("RGBA", p.size, (0, 0, 0, 0)); sh.putalpha(p.getchannel("A").point(lambda v: int(v * 0.5)))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    x, y = int(OW / 2 - p.size[0] / 2 + sx), int(OH / 2 - p.size[1] / 2 - 60 + sy)
    out.alpha_composite(sh, (x + 20, y + 30)); out.alpha_composite(p, (x, y))
    st = STAMP_T
    if t >= st:
        k = ease((t - st) / 0.16)
        sc = 1.9 - 0.9 * k
        s = LY["stamp"].resize((int(680 * sc * 0.95), int(330 * sc * 0.95)))
        a = s.getchannel("A").point(lambda v: int(v * k)); s.putalpha(a)
        out.alpha_composite(s, (OW // 2 - s.size[0] // 2 + 60, 1100 - s.size[1] // 2))

def scene4(t, out):
    z, cx, cy = cam(t, CUT4, CUTEND, 1.0, 1.18, (675, 1300), (640, 1380))
    for n, d in [("s4_sky", 0.3), ("s4_ships", 1.0), ("s4_sea", 1.0)]:
        zl = 1 + (z - 1) * d
        sink = (t - CUT4) * 12 if n == "s4_ships" else 0  # ships slowly settle into the sea
        place(LY[n], zl, cx, cy - sink, out)

def endcard(t, out):
    lt = t - CUTEND
    out.alpha_composite(Image.new("RGBA", (OW, OH), (20, 32, 46, 255)))
    k = ease(lt / 0.35)
    sc = 0.7 + 0.3 * k
    lg = LOGO.resize((int(560 * sc), int(560 * sc)))
    out.alpha_composite(lg, (OW // 2 - lg.size[0] // 2, 640 - lg.size[1] // 2))
    d = ImageDraw.Draw(out)
    f1 = ImageFont.truetype(FP_SC, 104); f2 = mfont(44)
    d.text((OW // 2, 1030), "BLUNDERBUSS", font=f1, fill=(241, 228, 200, int(255 * k)), anchor="mm")
    d.text((OW // 2, 1115), "@BlunderbussHistory", font=f2, fill=(201, 160, 74, int(255 * k)), anchor="mm")

FANTON = "/usr/share/fonts/truetype/anton/Anton-Regular.ttf"
import glob
FANTON = (glob.glob("/usr/share/fonts/**/Anton*.ttf", recursive=True) or [FANTON])[0]
FMONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
def mfont(size, w=b"Bold"):
    f = ImageFont.truetype(FMONT, size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
FP_SC = os.path.expanduser("~/.fonts/PlayfairSC-Black.ttf")

# ---------- captions ----------
CAP_LINES = [
    "In 1904, the Russian Navy went to war... with a fleet of British fishermen.",
    "Russia was fighting Japan, so it sent its Baltic Fleet halfway around the world.",
    "The crews were terrified of Japanese torpedo boats. And they saw them everywhere.",
    "Just before 1 a.m., on the Dogger Bank in the North Sea, they spotted small boats.",
    "Searchlights on. Guns firing.",
    "But these weren't torpedo boats. They were fishing trawlers from Hull, nets down, unable to run.",
    "The trawler Crane sank, and two fishermen were killed. In the chaos, Russian ships even hit one of their own.",
    "Britain and Russia came close to war. Russia paid £66,000.",
    "And the fleet? It sailed on to Japan... and was destroyed at Tsushima.",
    "Follow for more of history's biggest blunders.",
]
HL = {"1904,", "russian", "navy", "british", "fishermen.", "japan,", "baltic", "fleet", "torpedo", "boats.", "everywhere.",
      "dogger", "bank", "searchlights", "firing.", "hull,", "crane", "killed.", "own.", "war.", "£66,000.", "tsushima.", "blunders.", "japan..."}
chunks = []
for i, line in enumerate(CAP_LINES):
    words = line.split()
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[-1] in ".,?" :
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    # merge single short leftovers
    tot = sum(len(" ".join(g)) + 2 for g in groups)
    t0, t1 = timing[i]["start"], timing[i]["end"]
    acc = t0
    for g in groups:
        d = (t1 - t0) * (len(" ".join(g)) + 2) / tot
        chunks.append((acc, acc + d, g))
        acc += d
# stamp lands as "£66,000" is spoken
STAMP_T = [c for c in chunks if "£66,000." in c[2]][0][0] + 0.15

FC = ImageFont.truetype(FANTON, 104)
def cap_img(words):
    txt = [w.replace("...", "…").upper() for w in words]
    widths = [FC.getlength(w + " ") for w in txt]
    W = int(sum(widths)) + 60
    im = Image.new("RGBA", (W, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 30
    for w, raw, wd in zip(txt, words, widths):
        col = (255, 201, 74) if raw.lower() in HL else (255, 255, 255)
        d.text((x, 90), w, font=FC, fill=col, anchor="lm", stroke_width=9, stroke_fill=(10, 10, 14))
        x += wd
    if im.size[0] > OW - 80:
        r = (OW - 80) / im.size[0]; im = im.resize((int(im.size[0] * r), int(180 * r)), Image.LANCZOS)
    return im
CAPS = [(a, b, cap_img(g)) for a, b, g in chunks]

TAGS = [(0.2, CUT2, "OCTOBER 1904 · NORTH SEA"), (T[1], CUT2, "RUSSO-JAPANESE WAR"),
        (CUT2 + 0.1, T[6], "DOGGER BANK · 21–22 OCT"), (T[5], CUT3, "HULL TRAWLERS · NETS DOWN"),
        (T[6], CUT3, "TRAWLER 'CRANE' SUNK"), (CUT4 + 0.1, CUTEND, "TSUSHIMA · MAY 1905")]
FT = mfont(38, b"ExtraBold")
def tag(text):
    w = int(FT.getlength(text)) + 70
    im = Image.new("RGBA", (w, 76), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 75), 38, fill=(20, 32, 46, 225), outline=(201, 160, 74, 255), width=3)
    d.text((w // 2, 39), text, font=FT, fill=(241, 228, 200), anchor="mm")
    return im
TAGIM = [(a, b, tag(s)) for a, b, s in TAGS]

def frame(i):
    t = i / FPS
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 255))
    if t < CUT2: scene1(t, out)
    elif t < CUT3: scene2(t, out)
    elif t < CUT4: scene3(t, out)
    elif t < CUTEND: scene4(t, out)
    else: endcard(t, out)
    # vignette
    out.alpha_composite(VIG)
    # cut flash
    for c in (CUT2, CUT3, CUT4, CUTEND):
        if c <= t < c + 0.18:
            out.alpha_composite(Image.new("RGBA", (OW, OH), (255, 255, 255, int(150 * (1 - (t - c) / 0.18)))))
    # tags (latest active one)
    act = [x for x in TAGIM if x[0] <= t < x[1]]
    if act:
        a, b, im = act[-1]
        k = ease((t - a) / 0.2)
        out.alpha_composite(im, (OW // 2 - im.size[0] // 2, int(250 - 30 * (1 - k))))
    # captions
    if t < CUTEND + 0.1 or True:
        for a, b, im in CAPS:
            if a <= t < b + 0.05:
                k = ease((t - a) / 0.09)
                sc = 0.86 + 0.14 * k
                c = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))))
                y = 1330 if t < CUTEND else 1320
                out.alpha_composite(c, (OW // 2 - c.size[0] // 2, y - c.size[1] // 2))
                break
    return out.convert("RGB")

vg = np.zeros((OH, OW), np.float32)
yy, xx = np.mgrid[0:OH, 0:OW]
r = np.sqrt(((xx - OW / 2) / (OW * 0.75)) ** 2 + ((yy - OH / 2) / (OH * 0.7)) ** 2)
VIG = Image.fromarray(np.dstack([np.zeros_like(r)] * 3 + [np.clip((r - 0.55) * 300, 0, 170)]).astype(np.uint8), "RGBA")

if __name__ == "__main__":
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    if len(sys.argv) > 3:  # preview single frames
        for tt in sys.argv[3].split(","):
            frame(int(float(tt) * FPS)).save(f"video/prev_{tt}.jpg", quality=85)
        sys.exit()
    a, b = NF * part // nparts, NF * (part + 1) // nparts
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"video/part{part}.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    print("part", part, "done", a, b)
