import sys, random, math, os
sys.path.insert(0, "long")
import art
from art import *
art.OUT = "ep4/layers/"
os.makedirs(art.OUT, exist_ok=True)

BLACK, WHITE, BUFF = "#1A1A1C", "#E6E2D6", "#C8A060"

def ironclad(x, y, s, kind="victoria", flip=False, sil=None, smoke=True):
    """Victorian battleship, bow right, waterline at y. kind: victoria (single forward turret) / camperdown (barbettes fore & aft)."""
    hb, up, fn = (sil, sil, sil) if sil else (BLACK, WHITE, BUFF)
    sx = -s if flip else s
    g = f'<g transform="translate({x} {y}) scale({sx} {s})">'
    if smoke:
        g += f'<path d="M-10 -250 C -90 -320, -200 -340, -330 -360 C -220 -300, -120 -270, -60 -240 Z" fill="#6A6A6A" opacity="0.35" filter="url(#b6)"/>'
    # hull: low bow for victoria
    if kind == "victoria":
        g += f'<path d="M-330 0 L -320 -70 L 60 -70 L 60 -40 L 300 -36 L 340 0 Z" fill="{hb}"/>'
        g += f'<rect x="-250" y="-120" width="300" height="52" fill="{up}"/>'
        g += f'<ellipse cx="160" cy="-66" rx="80" ry="34" fill="{hb}"/><rect x="200" y="-82" width="200" height="16" fill="{hb}"/><rect x="200" y="-62" width="200" height="12" fill="{hb}"/>'
        g += f'<rect x="-310" y="-95" width="70" height="28" fill="{hb}"/><rect x="-360" y="-86" width="60" height="9" fill="{hb}"/>'
    else:
        g += f'<path d="M-330 0 L -320 -80 L 300 -80 L 340 0 Z" fill="{hb}"/>'
        g += f'<rect x="-200" y="-128" width="320" height="50" fill="{up}"/>'
        for bx in (-270, 230):
            g += f'<ellipse cx="{bx}" cy="-90" rx="55" ry="22" fill="{hb}"/><rect x="{bx-10}" y="-104" width="{120 if bx>0 else -0}" height="10" fill="{hb}"/>'
        g += f'<rect x="250" y="-104" width="120" height="10" fill="{hb}"/><rect x="-370" y="-104" width="110" height="10" fill="{hb}"/>'
    # funnels side by side, masts
    g += f'<rect x="-120" y="-250" width="44" height="132" fill="{fn}"/><rect x="-60" y="-250" width="44" height="132" fill="{fn}"/>'
    g += f'<rect x="-120" y="-258" width="44" height="12" fill="{hb}"/><rect x="-60" y="-258" width="44" height="12" fill="{hb}"/>'
    g += f'<rect x="-6" y="-360" width="10" height="242" fill="{hb}"/><rect x="-26" y="-300" width="50" height="16" fill="{hb}"/>'
    g += f'<rect x="-200" y="-300" width="8" height="180" fill="{hb}"/>'
    g += f'<rect x="20" y="-160" width="70" height="40" fill="{up}"/>'
    return g + '</g>'

def admiral(x, y, s, col="#141418"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-110 0 L -100 -250 C -95 -300, 95 -300, 100 -250 L 110 0 Z" fill="{col}"/>'
            f'<rect x="-120" y="-280" width="60" height="22" rx="8" fill="#C9A04A"/><rect x="60" y="-280" width="60" height="22" rx="8" fill="#C9A04A"/>'
            f'<circle cx="0" cy="-350" r="52" fill="{col}"/><path d="M-44 -330 C -40 -270, 40 -270, 44 -330 Z" fill="{col}"/>'
            f'<path d="M-62 -380 L 62 -380 L 56 -420 L -56 -420 Z" fill="{col}"/><path d="M-70 -378 L 80 -378 L 90 -366 L -60 -366 Z" fill="{col}"/>'
            f'<rect x="-30" y="-404" width="60" height="10" fill="#C9A04A"/></g>')

def officer(x, y, s, col="#141418", flip=False):
    sx = -s if flip else s
    return (f'<g transform="translate({x} {y}) scale({sx} {s})"><rect x="-26" y="-150" width="22" height="150" fill="{col}"/><rect x="4" y="-150" width="22" height="150" fill="{col}"/>'
            f'<path d="M-38 -150 L -40 -290 L 40 -290 L 38 -150 Z" fill="{col}"/><circle cx="0" cy="-318" r="27" fill="{col}"/>'
            f'<path d="M-30 -338 L 32 -338 L 30 -360 L -30 -360 Z" fill="{col}"/><path d="M-30 -338 L 46 -338 L 52 -330 L -30 -330 Z" fill="{col}"/>'
            f'<path d="M40 -270 L 90 -230 L 84 -220 L 36 -250 Z" fill="{col}"/></g>')

def boat(x, y, s, col="#141418"):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-120 0 L -110 -30 L 110 -30 L 130 0 Z" fill="{col}"/>'
            + "".join(f'<circle cx="{px}" cy="-50" r="10" fill="{col}"/><rect x="{px-8}" y="-44" width="16" height="16" fill="{col}"/><path d="M{px} -32 L {px+40} 10" stroke="{col}" stroke-width="5"/>' for px in (-70, -20, 30, 80))
            + '</g>')

# ---------- sprites ----------
save("victoria", ironclad(500, 600, 1.2, "victoria"), w=1000, h=760)            # waterline anchor (500, 600)
save("camperdown", ironclad(500, 600, 1.2, "camperdown"), w=1000, h=760)
save("victoria_hull", ironclad(500, 600, 1.2, "victoria", smoke=False), w=1000, h=760)
save("flash", '<circle cx="150" cy="150" r="150" fill="url(#fl)"/>', w=300, h=300,
     defs='<radialGradient id="fl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.3" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="#D9482B" stop-opacity="0"/></radialGradient>')
save("splash", '<path d="M40 300 C 60 200, 80 120, 100 20 C 115 100, 125 60, 140 10 C 150 110, 170 150, 200 70 C 205 170, 230 220, 260 300 Z" fill="#F0F4F6" opacity="0.9"/><ellipse cx="150" cy="300" rx="140" ry="22" fill="#F0F4F6" opacity="0.7"/>', w=300, h=330)
FLAGS = [("#D9482B", "#F1E4C8", "cross"), ("#2B5DA8", "#F1E4C8", "half"), ("#E8C040", "#1A1A1C", "ball"), ("#F1E4C8", "#D9482B", "diag")]
for i, (a, b, pat) in enumerate(FLAGS):
    inner = {"cross": f'<rect x="60" y="0" width="30" height="120" fill="{b}"/><rect x="0" y="45" width="150" height="30" fill="{b}"/>',
             "half": f'<rect x="75" y="0" width="75" height="120" fill="{b}"/>', "ball": f'<circle cx="75" cy="60" r="34" fill="{b}"/>',
             "diag": f'<path d="M0 0 L 150 120 L 150 90 L 30 0 Z" fill="{b}"/>'}[pat]
    save(f"flag{i}", f'<rect width="150" height="120" fill="{a}"/>{inner}<rect width="150" height="120" fill="none" stroke="#1A1A1C" stroke-width="4"/>', w=150, h=120)
save("ghost", officer(150, 420, 1.15, col="#DDE6F0"), w=300, h=440)
save("desk", '<rect width="2400" height="1350" fill="url(#dk2)"/>', defs='<radialGradient id="dk2" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3B2A1C"/><stop offset="1" stop-color="#120C08"/></radialGradient>')
save("man", '<circle cx="12" cy="10" r="9" fill="#141418"/><rect x="4" y="18" width="16" height="10" fill="#141418"/>', w=26, h=30)

# ---------- fleet (sunny Mediterranean, Lebanese coast) ----------
SKY = grad("sk", [(0, "#4F8CC0", 1), (1, "#E8EEF0", 1)]); SEA = grad("se", [(0, "#3A7AA0", 1), (1, "#0E2E44", 1)])
HZ = 760
mount = f'<path d="M0 {HZ} L 0 600 C 300 520, 500 560, 800 500 C 1100 440, 1300 540, 1600 520 C 1900 500, 2150 560, 2400 540 L 2400 {HZ} Z" fill="#9AA6B0" opacity="0.8"/>'
save("fleet_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{mount}<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>'
     + waves(HZ + 14, H, "#E8F4FA", 0.2, 34)
     + "".join(ironclad(x, HZ + 30, 0.42, "victoria" if i == 0 else "camperdown") for i, x in enumerate(range(2050, 0, -380)))
     + "".join(ironclad(x, HZ + 120, 0.6, "camperdown") for x in range(1900, 0, -480)),
     defs=SKY + SEA + BLUR)
save("fleet_front", waves(1150, H + 40, "#E8F4FA", 0.25, 50, seed=5))

# ---------- victoria close-up (low bow awash) ----------
save("victoria_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{mount}<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 14, H, "#E8F4FA", 0.2, 34), defs=SKY + SEA)
save("victoria_front", ironclad(1150, 1020, 2.2, "victoria") + f'<path d="M1500 1000 C 1600 960, 1750 950, 1950 990 L 1950 1030 L 1500 1030 Z" fill="#E8F4FA" opacity="0.7"/>'
     + f'<rect y="1020" width="{W}" height="{H-1020}" fill="url(#se2)"/>' + waves(1030, H, "#E8F4FA", 0.3, 40), defs=grad("se2", [(0, "#2F6A8E", 1), (1, "#0E2E44", 1)]))

# ---------- tryon ----------
save("tryon_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/><rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 14, H, "#E8F4FA", 0.2, 34)
     + ironclad(400, HZ + 20, 0.35, "camperdown") + ironclad(2000, HZ + 20, 0.3, "camperdown", flip=True), defs=SKY + SEA)
save("tryon_front", f'<rect x="0" y="1060" width="{W}" height="{H-1060}" fill="#2A2420"/><rect x="0" y="1040" width="{W}" height="24" fill="#C9A04A"/>'
     + admiral(1200, 1060, 1.9) + "".join(f'<rect x="{x}" y="900" width="14" height="150" fill="#2A2420"/>' for x in range(150, 2400, 300)) + f'<rect y="900" width="{W}" height="12" fill="#2A2420"/>')

# ---------- bridge (officers) ----------
save("bridge_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/><rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 14, H, "#E8F4FA", 0.2, 34)
     + "".join(ironclad(x, HZ + 25, 0.32, "camperdown", flip=True) for x in (1500, 1850, 2200)), defs=SKY + SEA)
save("bridge_front", f'<rect x="0" y="1080" width="{W}" height="{H-1080}" fill="#2A2420"/>' + "".join(f'<rect x="{x}" y="920" width="12" height="160" fill="#2A2420"/>' for x in range(100, 2400, 260))
     + f'<rect y="920" width="{W}" height="12" fill="#2A2420"/><rect y="990" width="{W}" height="6" fill="#2A2420"/>'
     + admiral(700, 1090, 1.3) + officer(1250, 1090, 1.3, flip=True) + officer(1600, 1090, 1.25)
     + f'<rect x="1900" y="930" width="70" height="160" fill="#2A2420"/><circle cx="1935" cy="920" r="44" fill="#C9A04A"/>')

# ---------- signals (mast; flags animated) ----------
save("signals_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/><rect y="{HZ+200}" width="{W}" height="{H-HZ-200}" fill="url(#se)"/>' + waves(HZ + 214, H, "#E8F4FA", 0.2, 34)
     + ironclad(2000, HZ + 260, 0.5, "camperdown", flip=True), defs=SKY + SEA)
save("signals_front", f'<rect x="1080" y="0" width="34" height="{H}" fill="#2A2420"/><rect x="760" y="230" width="700" height="18" fill="#2A2420"/>'
     + f'<path d="M780 248 L 780 {H}" stroke="#2A2420" stroke-width="3"/><path d="M1440 248 L 1440 {H}" stroke="#2A2420" stroke-width="3"/>')

# ---------- diagrams (plan view, drawn live) ----------
save("chart", f'<rect width="{W}" height="{H}" fill="#C8D8DE"/>'
     + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#7A9AA6" stroke-width="2" opacity="0.4"/>' for x in range(0, W + 1, 150))
     + "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#7A9AA6" stroke-width="2" opacity="0.4"/>' for y in range(0, H + 1, 150))
     + f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="#2A4A56" stroke-width="6"/>'
     + f'<text x="{W-90}" y="{H-80}" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="34" fill="#2A4A56" text-anchor="end">plan view · simplified, not to scale</text>')

# ---------- collision / sinking (open sea, calm) ----------
save("sea_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{mount}<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 14, H, "#E8F4FA", 0.2, 34)
     + "".join(ironclad(x, HZ + 15, 0.25, "camperdown") for x in (300, 600, 2100)), defs=SKY + SEA + BLUR)
save("sea_front", f'<rect y="1010" width="{W}" height="{H-1010}" fill="url(#sf)"/>' + waves(1020, H, "#E8F4FA", 0.3, 40),
     defs=grad("sf", [(0, "#2F6A8E", 0.97), (1, "#0E2E44", 1)]))

# ---------- rescue (evening) ----------
save("rescue_back", f'<rect width="{W}" height="{H}" fill="url(#ev)"/><circle cx="1800" cy="740" r="140" fill="#FFD090" opacity="0.9"/>'
     + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#es)"/>' + waves(HZ + 14, H, "#FFD8B0", 0.2, 34)
     + "".join(ironclad(x, HZ + 20, 0.35, "camperdown", sil="#2A2030") for x in (500, 1100, 2150)),
     defs=grad("ev", [(0, "#3A3A5A", 1), (1, "#E8A070", 1)]) + grad("es", [(0, "#6A4A5A", 1), (1, "#141420", 1)]))
save("rescue_front", boat(800, 1080, 1.5) + boat(1500, 1150, 1.8) + boat(300, 1000, 1.0) + waves(1050, H, "#FFD8B0", 0.25, 46, seed=3))

# ---------- documents ----------
def document(name, l1, l2, l3, seed):
    PW, PH = 1150, 1500
    r = random.Random(seed); lines = ""; y = 560
    while y < PH - 120:
        lines += f'<rect x="110" y="{y}" width="{r.choice([930, 930, 880, 820, 600])}" height="10" rx="5" fill="#3A3226" opacity="0.5"/>'; y += 34
    save(name, f'<rect width="{PW}" height="{PH}" fill="#E8DCC0"/><rect x="30" y="30" width="{PW-60}" height="{PH-60}" fill="none" stroke="#5A4630" stroke-width="4"/>'
         f'<text x="{PW/2}" y="200" font-family="Playfair Display" font-style="italic" font-weight="900" font-size="80" fill="#2A1E14" text-anchor="middle">{l1}</text>'
         f'<text x="{PW/2}" y="290" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="46" fill="#2A1E14" text-anchor="middle">{l2}</text>'
         f'<text x="{PW/2}" y="370" font-family="Playfair Display SC" font-weight="900" font-size="40" fill="#5A4630" text-anchor="middle">{l3}</text>'
         f'<line x1="200" y1="420" x2="{PW-200}" y2="420" stroke="#5A4630" stroke-width="3"/>{lines}', w=PW, h=PH)
document("court", "Court Martial", "on the loss of H.M.S. Victoria", "JULY 1893", 41)
newspaper("paper", "JULY 1893", "LOSS OF THE", "VICTORIA", "Court martial blames the", "admiral's turning signal", seed=42)

# ---------- ghost (Victorian drawing room) ----------
save("ghost_back", f'<rect width="{W}" height="{H}" fill="#2A1E22"/>'
     + f'<rect x="300" y="200" width="380" height="600" fill="#4A5A7A" opacity="0.6"/><rect x="480" y="200" width="16" height="600" fill="#2A1E22"/><rect x="300" y="490" width="380" height="14" fill="#2A1E22"/>'
     + f'<rect x="1600" y="560" width="500" height="400" fill="#1A1216"/><rect x="1700" y="700" width="300" height="260" fill="#C86A3A" opacity="0.8"/>'
     + f'<circle cx="1850" cy="800" r="200" fill="#E89A5A" opacity="0.15" filter="url(#b40)"/>'
     + f'<rect y="1080" width="{W}" height="{H-1080}" fill="#1A1014"/>', defs=BLUR)
guests = "".join(officer(x, 1110, 1.2, col="#0E080A", flip=(i % 2 == 0)).replace("officer", "") for i, x in enumerate((250, 2250)))
dresses = "".join(f'<g transform="translate({x} 1110) scale(1.2)"><path d="M-80 0 L -30 -200 L 30 -200 L 80 0 Z" fill="#0E080A"/><path d="M-26 -200 L -22 -290 L 22 -290 L 26 -200 Z" fill="#0E080A"/><circle cx="0" cy="-316" r="26" fill="#0E080A"/></g>' for x in (900, 1450, 2000))
save("ghost_front", guests + dresses)

# ---------- jellicoe (grey North Sea, dreadnought line) ----------
save("jellicoe_back", f'<rect width="{W}" height="{H}" fill="url(#gy)"/>' + fog(300, 700, 10, col="#9AA0A4", op=(0.3, 0.5))
     + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="#4A5660"/>' + waves(HZ + 14, H, "#D8E0E4", 0.15, 34)
     + "".join(battleship(x, HZ + 12, s, col="#2A3036", lights=False, smoke="#4A5056") for x, s in [(2100, 0.9), (1550, 0.75), (1100, 0.62), (720, 0.52), (420, 0.44), (160, 0.38)]),
     defs=grad("gy", [(0, "#6A747C", 1), (1, "#B8BEC2", 1)]) + BLUR)
save("jellicoe_front", "")

# ---------- wreck (deep, vertical) ----------
save("wreck_back", f'<rect width="{W}" height="{H}" fill="url(#dp)"/>'
     + f'<path d="M0 1100 C 600 1060, 1600 1080, 2400 1070 L 2400 {H} L 0 {H} Z" fill="#141A1C"/>',
     defs=grad("dp", [(0, "#0E2E3A", 1), (1, "#02080A", 1)]))
save("wreck_front", "".join(f'<polygon points="{x},0 {x+40},0 {x+260},{H} {x-180},{H}" fill="#9AD0D8" opacity="0.06"/>' for x in (700, 1500))
     + f'<g transform="rotate(-90 1200 1180)">{ironclad(1200, 1180, 1.9, "victoria", smoke=False, sil="#22363C")}</g>'
     + f'<path d="M0 1120 C 600 1080, 1600 1110, 2400 1090 L 2400 {H} L 0 {H} Z" fill="#0E1416"/>' + fog(800, 1200, 8, col="#1A3A40", op=(0.2, 0.35)))
print("ep4 scenes done")
