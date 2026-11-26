"""Draws the illustrated layers for the Dogger Bank short as SVG -> PNG (1350x2400, 1.25x of 1080x1920)."""
import subprocess, random, math, os
os.makedirs("video/layers", exist_ok=True)
W, H = 1350, 2400
NAVY, CREAM, RED, BRASS = "#14202E", "#F1E4C8", "#D9482B", "#C9A04A"

def save(name, body, w=W, h=H, defs=""):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'
    open(f"video/layers/{name}.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", f"video/layers/{name}.svg", "-o", f"video/layers/{name}.png"], check=True)

BLUR = '<filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>' \
       '<filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>' \
       '<filter id="b40" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'

def battleship(x, y, s, col="#060B12", lights=True, smoke="#3A4656"):
    # pre-dreadnought silhouette, bow to the right, waterline at y
    g = f'<g transform="translate({x} {y}) scale({s})">'
    g += f'<path d="M-40 -190 C -120 -260, -200 -300, -330 -330 C -230 -270, -170 -230, -120 -190 Z" fill="{smoke}" opacity="0.55" filter="url(#b6)"/>'
    g += f'<path d="M60 -190 C -10 -270, -90 -310, -220 -350 C -110 -280, -50 -240, -10 -190 Z" fill="{smoke}" opacity="0.5" filter="url(#b6)"/>'
    g += (f'<path d="M-300 0 L -290 -38 L -200 -44 L -200 -70 L 200 -70 L 200 -44 L 300 -40 L 330 0 Z" fill="{col}"/>'
          f'<rect x="-150" y="-110" width="300" height="42" fill="{col}"/>'
          f'<rect x="-60" y="-200" width="34" height="95" fill="{col}"/><rect x="40" y="-200" width="34" height="95" fill="{col}"/>'
          f'<rect x="-175" y="-260" width="9" height="200" fill="{col}"/><rect x="145" y="-280" width="9" height="215" fill="{col}"/>'
          f'<rect x="-190" y="-200" width="40" height="14" fill="{col}"/><rect x="128" y="-215" width="44" height="14" fill="{col}"/>'
          f'<path d="M-260 -44 L -230 -86 L -180 -86 L -170 -44 Z" fill="{col}"/><path d="M190 -44 L 200 -86 L 250 -86 L 270 -44 Z" fill="{col}"/>'
          f'<rect x="-300" y="-72" width="60" height="9" fill="{col}"/><rect x="250" y="-72" width="70" height="9" fill="{col}"/>')
    if lights:
        g += '<circle cx="150" cy="-282" r="5" fill="#FFE7A8"/><circle cx="-171" cy="-262" r="4" fill="#FFE7A8"/><circle cx="250" cy="-30" r="4" fill="#E9533A"/>'
    return g + '</g>'

def trawler(x, y, s, col="#0A1119", lights=True, flip=False):
    sx = -s if flip else s
    g = f'<g transform="translate({x} {y}) scale({sx} {s})">'
    g += (f'<path d="M-150 0 L -165 -50 L -60 -46 L 120 -52 L 175 -78 L 150 0 Z" fill="{col}"/>'
          f'<rect x="-40" y="-110" width="70" height="60" fill="{col}"/>'
          f'<rect x="-15" y="-190" width="20" height="90" fill="{col}"/><rect x="-15" y="-170" width="20" height="10" fill="{BRASS}" opacity="0.6"/>'
          f'<rect x="95" y="-260" width="6" height="210" fill="{col}"/><rect x="-125" y="-200" width="6" height="150" fill="{col}"/>'
          f'<path d="M-119 -195 L -60 -80 L -119 -80 Z" fill="{col}" opacity="0.9"/>'
          f'<path d="M100 -60 L 60 -20 M -110 -50 L -150 -10" stroke="{col}" stroke-width="5"/>'
          f'<path d="M-150 -8 C -200 40, -260 70, -330 90" stroke="{col}" stroke-width="3" fill="none" opacity="0.8"/>')
    if lights:
        g += ('<circle cx="98" cy="-255" r="6" fill="#FFF4D0"/><circle cx="98" cy="-200" r="5" fill="#E9533A"/>'
              '<circle cx="-20" cy="-80" r="5" fill="#4CD08A"/><circle cx="20" cy="-80" r="5" fill="#E9533A"/>')
    return g + '</g>'

random.seed(4)
def stars(n, ymax, op=(0.2, 0.8)):
    return "".join(f'<circle cx="{random.randint(0,W)}" cy="{random.randint(0,ymax)}" r="{random.choice([1.5,2,2.5,3,3.5])}" fill="{CREAM}" opacity="{random.uniform(*op):.2f}"/>' for _ in range(n))

def waves(y0, y1, col, op, step=46):
    out = ""
    rows = range(y0, y1, step)
    for i, y in enumerate(rows):
        off = (i * 37) % 120
        amp = 6 + (y - y0) / (y1 - y0) * 18
        seg = 60 + (y - y0) / (y1 - y0) * 120
        d = f"M{-off} {y}"
        x = -off
        while x < W + 200:
            d += f" q {seg/2:.0f} {-amp:.0f} {seg:.0f} 0"
            x += seg
        out += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2+ (y-y0)/(y1-y0)*5:.1f}" opacity="{op}"/>'
    return out

# ---------------- SCENE 1: the fleet at night ----------------
HZ = 1450
sky = (f'<linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060C14"/><stop offset="0.55" stop-color="#14253A"/><stop offset="1" stop-color="#2C4258"/></linearGradient>'
       f'<radialGradient id="moon" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.45"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></radialGradient>')
save("s1_sky", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{stars(220, HZ-150)}'
     f'<circle cx="1010" cy="520" r="260" fill="url(#moon)"/><circle cx="1010" cy="520" r="78" fill="{CREAM}"/>'
     f'<circle cx="985" cy="500" r="14" fill="#D8C9A8" opacity="0.6"/><circle cx="1035" cy="545" r="10" fill="#D8C9A8" opacity="0.5"/>', defs=sky + BLUR)
ships = "".join(battleship(x, HZ + 6, s) for x, s in [(1060, 1.45), (430, 0.95), (70, 0.62)])
save("s1_ships", ships, defs=BLUR)
fog = "".join(f'<ellipse cx="{random.randint(-100,W+100)}" cy="{random.randint(HZ-260, HZ+120)}" rx="{random.randint(260,520)}" ry="{random.randint(40,90)}" fill="#9AA9B8" opacity="{random.uniform(0.10,0.22):.2f}" filter="url(#b40)"/>' for _ in range(16))
save("s1_fog", fog, defs=BLUR)
sea = (f'<linearGradient id="se" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A2B3D"/><stop offset="1" stop-color="#05090F"/></linearGradient>'
       f'<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.55"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></linearGradient>')
save("s1_sea", f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>'
     f'<path d="M960 {HZ} L 1060 {HZ} L 1180 {H} L 840 {H} Z" fill="url(#refl)" opacity="0.5" filter="url(#b20)"/>'
     + waves(HZ + 20, H, "#7F95AA", 0.22), defs=sea + BLUR)

# ---------------- SCENE 2: searchlights on the trawlers ----------------
HZ2 = 1250
sky2 = (f'<linearGradient id="sk2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05090E"/><stop offset="1" stop-color="#1B2B3C"/></linearGradient>')
save("s2_sky", f'<rect width="{W}" height="{H}" fill="url(#sk2)"/>{stars(90, HZ2-300, (0.1, 0.4))}'
     + "".join(battleship(x, HZ2 + 4, s, col="#03070C", smoke="#22303E") for x, s in [(-60, 0.5), (230, 0.36), (420, 0.27)]), defs=sky2 + BLUR)
sea2 = (f'<linearGradient id="se2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#17283A"/><stop offset="1" stop-color="#04080D"/></linearGradient>')
save("s2_sea", f'<rect y="{HZ2}" width="{W}" height="{H-HZ2}" fill="url(#se2)"/>' + waves(HZ2 + 20, H, "#6F879E", 0.2), defs=sea2)
save("s2_trawlers_far", trawler(820, HZ2 + 150, 0.75) + trawler(1180, HZ2 + 110, 0.55, flip=True) + trawler(560, HZ2 + 90, 0.45))
save("s2_crane", trawler(0, 0, 1.6), w=700, h=520) if False else None
# Crane drawn on its own canvas so it can tilt/sink; waterline at (350, 430)
crane_svg = f'<g transform="translate(-0 0)">{trawler(380, 430, 1.55)}</g>'
save("s2_crane", crane_svg, w=760, h=560)
fg_waves = (f'<linearGradient id="fw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B1520" stop-opacity="0"/><stop offset="0.25" stop-color="#0B1520"/><stop offset="1" stop-color="#03060A"/></linearGradient>')
save("s2_fg", f'<rect y="1900" width="{W}" height="{H-1900}" fill="url(#fw)"/>' + waves(1960, H, "#8AA2B8", 0.25, step=60), defs=fg_waves)
# searchlight beam (origin at left-middle of its canvas)
beam = (f'<linearGradient id="bm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF6DA" stop-opacity="0.85"/><stop offset="0.6" stop-color="#FFF6DA" stop-opacity="0.25"/><stop offset="1" stop-color="#FFF6DA" stop-opacity="0"/></linearGradient>')
save("beam", f'<polygon points="0,200 1800,0 1800,400" fill="url(#bm)" filter="url(#b6)"/>', w=1800, h=400, defs=beam + BLUR)
# muzzle flash + shell splash sprites
fl = (f'<radialGradient id="fl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.3" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>')
save("flash", f'<circle cx="150" cy="150" r="150" fill="url(#fl)"/>', w=300, h=300, defs=fl)
spl = f'<path d="M40 300 C 60 200, 80 120, 100 20 C 115 100, 125 60, 140 10 C 150 110, 170 150, 200 70 C 205 170, 230 220, 260 300 Z" fill="#E8EEF3" opacity="0.9"/><ellipse cx="150" cy="300" rx="140" ry="22" fill="#E8EEF3" opacity="0.7"/>'
save("splash", spl, w=300, h=330)

# ---------------- SCENE 3: newspaper ----------------
PW, PH = 1150, 1650
random.seed(11)
lines = ""
for col in range(3):
    x0 = 70 + col * 350
    y = 760 if col else 1000
    while y < PH - 90:
        wln = random.choice([300, 300, 300, 260, 220])
        lines += f'<rect x="{x0}" y="{y}" width="{wln}" height="11" rx="3" fill="#3A3226" opacity="0.55"/>'
        y += 27
        if random.random() < 0.08:
            y += 25
paper = (f'<rect width="{PW}" height="{PH}" fill="#EADBB8"/>'
         f'<rect x="20" y="20" width="{PW-40}" height="{PH-40}" fill="none" stroke="#3A3226" stroke-width="3" opacity="0.6"/>'
         f'<text x="{PW/2}" y="150" font-family="Playfair Display SC" font-weight="900" font-size="74" fill="#1B1712" text-anchor="middle">BLUNDERBUSS GAZETTE</text>'
         f'<line x1="60" y1="185" x2="{PW-60}" y2="185" stroke="#1B1712" stroke-width="4"/>'
         f'<text x="{PW/2}" y="225" font-family="Playfair Display" font-weight="600" font-size="30" fill="#1B1712" text-anchor="middle" letter-spacing="3">MONDAY, OCTOBER 24, 1904  ·  ONE PENNY</text>'
         f'<line x1="60" y1="250" x2="{PW-60}" y2="250" stroke="#1B1712" stroke-width="2"/>'
         f'<text x="{PW/2}" y="420" font-family="Playfair Display" font-weight="900" font-size="150" fill="#1B1712" text-anchor="middle">THE RUSSIAN</text>'
         f'<text x="{PW/2}" y="570" font-family="Playfair Display" font-weight="900" font-size="150" fill="#1B1712" text-anchor="middle">OUTRAGE</text>'
         f'<text x="{PW/2}" y="660" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="44" fill="#1B1712" text-anchor="middle">Baltic Fleet fires on Hull trawlers</text>'
         f'<text x="{PW/2}" y="715" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="44" fill="#1B1712" text-anchor="middle">on the Dogger Bank</text>'
         f'<rect x="70" y="760" width="300" height="220" fill="#3A3226" opacity="0.18"/>'
         + trawler(220, 940, 0.6, col="#3A3226", lights=False) + lines)
save("s3_paper", paper, w=PW, h=PH)
desk = (f'<radialGradient id="dk" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3B2A1C"/><stop offset="1" stop-color="#120C08"/></radialGradient>')
save("s3_desk", f'<rect width="{W}" height="{H}" fill="url(#dk)"/>', defs=desk)
stamp = (f'<g transform="rotate(-12 330 130)"><rect x="20" y="20" width="620" height="220" rx="18" fill="none" stroke="{RED}" stroke-width="14"/>'
         f'<text x="330" y="150" font-family="Anton" font-size="120" fill="{RED}" text-anchor="middle">£66,000</text>'
         f'<text x="330" y="215" font-family="Montserrat" font-weight="800" font-size="42" fill="{RED}" text-anchor="middle" letter-spacing="8">COMPENSATION</text></g>')
save("stamp", stamp, w=680, h=330)

# ---------------- SCENE 4: Tsushima ----------------
HZ4 = 1500
sky4 = (f'<linearGradient id="sk4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A0B0A"/><stop offset="0.6" stop-color="#7A2216"/><stop offset="1" stop-color="#E0602F"/></linearGradient>')
smoke = "".join(f'<ellipse cx="{x}" cy="{HZ4-300-random.randint(0,500)}" rx="{random.randint(120,260)}" ry="{random.randint(80,160)}" fill="#1A1110" opacity="{random.uniform(0.35,0.6):.2f}" filter="url(#b40)"/>' for x in range(-50, W+100, 120))
save("s4_sky", f'<rect width="{W}" height="{H}" fill="url(#sk4)"/>{smoke}', defs=sky4 + BLUR)
fire = f'<radialGradient id="fi" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFD27A"/><stop offset="0.4" stop-color="#FF7A2E" stop-opacity="0.8"/><stop offset="1" stop-color="#FF7A2E" stop-opacity="0"/></radialGradient>'
s4 = ""
for (x, s, rot) in [(980, 0.9, 14), (420, 0.6, -18), (150, 0.4, 8)]:
    s4 += f'<g transform="rotate({rot} {x} {HZ4})"><circle cx="{x-20}" cy="{HZ4-120*s}" r="{170*s}" fill="url(#fi)"/>{battleship(x, HZ4 + 60*s, s, col="#0C0605", lights=False, smoke="#120B0A")}</g>'
save("s4_ships", s4, defs=fire + BLUR)
sea4 = f'<linearGradient id="se4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A1610"/><stop offset="1" stop-color="#070303"/></linearGradient>'
save("s4_sea", f'<rect y="{HZ4}" width="{W}" height="{H-HZ4}" fill="url(#se4)"/>' + waves(HZ4 + 20, H, "#E0602F", 0.18), defs=sea4)
print("layers done")
