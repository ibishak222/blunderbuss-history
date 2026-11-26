"""Shared drawing helpers (SVG strings) for the 16:9 episode. Canvas is 2400x1350 (1.25x of 1920x1080)."""
import random, subprocess, os
W, H = 2400, 1350
NAVY, CREAM, RED, BRASS = "#14202E", "#F1E4C8", "#D9482B", "#C9A04A"
OUT = "long/layers/"
os.makedirs(OUT, exist_ok=True)

BLUR = ('<filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>'
        '<filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>'
        '<filter id="b40" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>')

def save(name, body, w=W, h=H, defs=""):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{BLUR}{defs}</defs>{body}</svg>'
    open(f"{OUT}{name}.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", f"{OUT}{name}.svg", "-o", f"{OUT}{name}.png"], check=True)

def grad(id, stops, vertical=True):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<linearGradient id="{id}" {xy}>{s}</linearGradient>'

def battleship(x, y, s, col="#060B12", lights=True, smoke="#3A4656", flip=False, windows=False):
    sx = -s if flip else s
    g = f'<g transform="translate({x} {y}) scale({sx} {s})">'
    if smoke:
        g += f'<path d="M-40 -190 C -120 -260, -200 -300, -330 -330 C -230 -270, -170 -230, -120 -190 Z" fill="{smoke}" opacity="0.55" filter="url(#b6)"/>'
        g += f'<path d="M60 -190 C -10 -270, -90 -310, -220 -350 C -110 -280, -50 -240, -10 -190 Z" fill="{smoke}" opacity="0.5" filter="url(#b6)"/>'
    g += (f'<path d="M-300 0 L -290 -38 L -200 -44 L -200 -70 L 200 -70 L 200 -44 L 300 -40 L 330 0 Z" fill="{col}"/>'
          f'<rect x="-150" y="-110" width="300" height="42" fill="{col}"/>'
          f'<rect x="-60" y="-200" width="34" height="95" fill="{col}"/><rect x="40" y="-200" width="34" height="95" fill="{col}"/>'
          f'<rect x="-175" y="-260" width="9" height="200" fill="{col}"/><rect x="145" y="-280" width="9" height="215" fill="{col}"/>'
          f'<rect x="-190" y="-200" width="40" height="14" fill="{col}"/><rect x="128" y="-215" width="44" height="14" fill="{col}"/>'
          f'<path d="M-260 -44 L -230 -86 L -180 -86 L -170 -44 Z" fill="{col}"/><path d="M190 -44 L 200 -86 L 250 -86 L 270 -44 Z" fill="{col}"/>'
          f'<rect x="-300" y="-72" width="60" height="9" fill="{col}"/><rect x="250" y="-72" width="70" height="9" fill="{col}"/>')
    if windows:
        g += "".join(f'<rect x="{x0}" y="-30" width="10" height="7" fill="#FFD98A" opacity="0.9"/>' for x0 in range(-240, 260, 34))
    if lights:
        g += '<circle cx="150" cy="-282" r="5" fill="#FFE7A8"/><circle cx="-171" cy="-262" r="4" fill="#FFE7A8"/><circle cx="250" cy="-30" r="4" fill="#E9533A"/>'
    return g + '</g>'

def cruiser3(x, y, s, col="#060B12", windows=False):
    """three-funnel cruiser (Aurora-like silhouette, generic)"""
    g = f'<g transform="translate({x} {y}) scale({s})">'
    g += (f'<path d="M-340 0 L -330 -34 L 300 -40 L 350 0 Z" fill="{col}"/>'
          f'<rect x="-200" y="-80" width="380" height="42" fill="{col}"/>'
          + "".join(f'<rect x="{fx}" y="-190" width="30" height="115" fill="{col}"/>' for fx in (-110, -30, 50))
          + f'<rect x="-250" y="-270" width="8" height="230" fill="{col}"/><rect x="200" y="-260" width="8" height="220" fill="{col}"/>'
          f'<rect x="150" y="-110" width="60" height="32" fill="{col}"/><rect x="-260" y="-100" width="70" height="26" fill="{col}"/>')
    if windows:
        g += "".join(f'<rect x="{x0}" y="-24" width="9" height="7" fill="#FFD98A" opacity="0.85"/>' for x0 in range(-300, 300, 30))
    return g + '</g>'

def merchant(x, y, s, col="#070C13", flip=False):
    sx = -s if flip else s
    return (f'<g transform="translate({x} {y}) scale({sx} {s})">'
            f'<path d="M-260 0 L -275 -60 L 250 -60 L 290 -90 L 270 0 Z" fill="{col}"/>'
            f'<rect x="-60" y="-130" width="150" height="72" fill="{col}"/><rect x="0" y="-220" width="40" height="95" fill="{col}"/>'
            f'<rect x="-190" y="-230" width="9" height="175" fill="{col}"/><rect x="180" y="-240" width="9" height="185" fill="{col}"/>'
            f'<path d="M-186 -220 L -110 -80" stroke="{col}" stroke-width="8"/><path d="M184 -230 L 120 -80" stroke="{col}" stroke-width="8"/>'
            f'<circle cx="184" cy="-236" r="5" fill="#FFE7A8"/></g>')

def schooner(x, y, s, col="#0A1119"):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-120 0 L -130 -30 L 130 -30 L 150 -50 L 120 0 Z" fill="{col}"/>'
            f'<rect x="-50" y="-260" width="7" height="235" fill="{col}"/><rect x="40" y="-230" width="7" height="205" fill="{col}"/>'
            f'<path d="M-46 -255 L -46 -40 L 30 -40 Z" fill="{col}" opacity="0.85"/><path d="M44 -225 L 44 -40 L 120 -40 Z" fill="{col}" opacity="0.85"/></g>')

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

def stars(n, ymax, op=(0.2, 0.8), seed=1):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(0,ymax)}" r="{r.choice([1.5,2,2.5,3])}" fill="{CREAM}" opacity="{r.uniform(*op):.2f}"/>' for _ in range(n))

def waves(y0, y1, col, op, step=40, seed=0):
    out = ""
    for i, y in enumerate(range(y0, y1, step)):
        f = (y - y0) / max(1, (y1 - y0))
        off = (i * 37 + seed) % 120
        amp, seg = 5 + f * 14, 70 + f * 130
        d, x = f"M{-off} {y}", -off
        while x < W + 200:
            d += f" q {seg/2:.0f} {-amp:.0f} {seg:.0f} 0"; x += seg
        out += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2 + f*4:.1f}" opacity="{op}"/>'
    return out

def fog(y0, y1, n, col="#9AA9B8", op=(0.1, 0.22), seed=3):
    r = random.Random(seed)
    return "".join(f'<ellipse cx="{r.randint(-100,W+100)}" cy="{r.randint(y0,y1)}" rx="{r.randint(300,700)}" ry="{r.randint(40,90)}" fill="{col}" opacity="{r.uniform(*op):.2f}" filter="url(#b40)"/>' for _ in range(n))

def palm(x, y, s, col="#120A08"):
    leaves = "".join(f'<path d="M0 -300 Q {dx*0.5} {-330+dy*0.3}, {dx} {-300+dy}" stroke="{col}" stroke-width="16" fill="none" stroke-linecap="round"/>'
                     for dx, dy in [(-170, 40), (-140, 110), (160, 50), (130, 120), (-60, -60), (70, -50), (10, 150)])
    return f'<g transform="translate({x} {y}) scale({s})"><path d="M-10 0 Q 20 -150, 0 -300" stroke="{col}" stroke-width="22" fill="none"/>{leaves}</g>'

def newspaper(name, masthead_date, head1, head2, sub1, sub2, seed=11):
    PW, PH = 1150, 1500
    r = random.Random(seed)
    lines = ""
    for col in range(3):
        x0 = 70 + col * 350
        y = 760 if col else 1000
        while y < PH - 90:
            lines += f'<rect x="{x0}" y="{y}" width="{r.choice([300,300,300,260,220])}" height="11" rx="3" fill="#3A3226" opacity="0.55"/>'
            y += 27 + (25 if r.random() < 0.08 else 0)
    body = (f'<rect width="{PW}" height="{PH}" fill="#EADBB8"/>'
            f'<rect x="20" y="20" width="{PW-40}" height="{PH-40}" fill="none" stroke="#3A3226" stroke-width="3" opacity="0.6"/>'
            f'<text x="{PW/2}" y="150" font-family="Playfair Display SC" font-weight="900" font-size="74" fill="#1B1712" text-anchor="middle">BLUNDERBUSS GAZETTE</text>'
            f'<line x1="60" y1="185" x2="{PW-60}" y2="185" stroke="#1B1712" stroke-width="4"/>'
            f'<text x="{PW/2}" y="225" font-family="Playfair Display" font-weight="600" font-size="30" fill="#1B1712" text-anchor="middle" letter-spacing="3">{masthead_date}  ·  ONE PENNY</text>'
            f'<line x1="60" y1="250" x2="{PW-60}" y2="250" stroke="#1B1712" stroke-width="2"/>'
            f'<text x="{PW/2}" y="420" font-family="Playfair Display" font-weight="900" font-size="{150 if len(head1)<12 else 118}" fill="#1B1712" text-anchor="middle">{head1}</text>'
            f'<text x="{PW/2}" y="570" font-family="Playfair Display" font-weight="900" font-size="{150 if len(head2)<12 else 118}" fill="#1B1712" text-anchor="middle">{head2}</text>'
            f'<text x="{PW/2}" y="660" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="44" fill="#1B1712" text-anchor="middle">{sub1}</text>'
            f'<text x="{PW/2}" y="715" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="44" fill="#1B1712" text-anchor="middle">{sub2}</text>'
            f'<rect x="70" y="760" width="300" height="220" fill="#3A3226" opacity="0.18"/>' + lines)
    save(name, body, w=PW, h=PH)
