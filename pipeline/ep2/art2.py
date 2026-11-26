"""Episode 2 drawing helpers: emus, soldiers, Lewis gun, truck, farm pieces. Canvas 2400x1350."""
import sys, random, math
sys.path.insert(0, "long")
import art
from art import *
art.OUT = "ep2/layers/"
import os; os.makedirs(art.OUT, exist_ok=True)

SIL = "#1A120E"

def emu(x, y, s, pose="stand", col=SIL, flip=False):
    """Emu silhouette, feet at (x,y), facing right (flip=True faces left). ~400 units tall at s=1."""
    sx = -s if flip else s
    g = f'<g transform="translate({x} {y}) scale({sx} {s})">'
    body = ('<path d="M-135 -205 C -135 -295, 55 -305, 92 -235 C 104 -205, 84 -158, 44 -146 L 34 -122 L 14 -144 L -8 -118 L -30 -142 '
            'L -52 -120 L -74 -144 L -98 -124 L -114 -152 C -128 -166, -135 -184, -135 -205 Z" fill="{c}"/>').format(c=col)
    legs = {
        "stand": [((0, -140), (6, -72), (0, 0)), ((-32, -140), (-28, -72), (-36, 0))],
        "peck":  [((0, -140), (6, -72), (0, 0)), ((-32, -140), (-28, -72), (-36, 0))],
        "run0":  [((0, -140), (46, -82), (82, -22)), ((-32, -140), (-62, -72), (-122, -46))],
        "run1":  [((0, -140), (22, -70), (12, 0)), ((-32, -140), (-12, -76), (-66, -36))],
        "run2":  [((0, -140), (-30, -74), (-92, -46)), ((-32, -140), (14, -84), (52, -22))],
        "run3":  [((0, -140), (-4, -78), (-50, -32)), ((-32, -140), (-6, -72), (-18, 0))],
    }[pose]
    lg = ""
    for (a, b, c) in legs:
        lg += f'<path d="M{a[0]} {a[1]} L {b[0]} {b[1]} L {c[0]} {c[1]}" stroke="{col}" stroke-width="13" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
        lg += f'<path d="M{c[0]-14} {c[1]+2} L {c[0]+30} {c[1]+2}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>'
    if pose == "peck":
        neck = f'<path d="M70 -235 C 120 -220, 150 -150, 168 -70" stroke="{col}" stroke-width="20" fill="none" stroke-linecap="round"/>'
        head = f'<ellipse cx="172" cy="-58" rx="17" ry="14" fill="{col}"/><path d="M176 -50 L 184 -22 L 166 -48 Z" fill="{col}"/>'
    elif pose.startswith("run"):
        neck = f'<path d="M64 -246 C 104 -280, 128 -320, 150 -352" stroke="{col}" stroke-width="20" fill="none" stroke-linecap="round"/>'
        head = f'<ellipse cx="156" cy="-360" rx="19" ry="14" fill="{col}"/><path d="M170 -364 L 200 -356 L 170 -352 Z" fill="{col}"/>'
    else:
        neck = f'<path d="M60 -244 C 86 -292, 96 -342, 104 -384" stroke="{col}" stroke-width="20" fill="none" stroke-linecap="round"/>'
        head = f'<ellipse cx="110" cy="-392" rx="19" ry="14" fill="{col}"/><path d="M124 -396 L 154 -388 L 124 -384 Z" fill="{col}"/>'
    return g + lg + body + neck + head + '</g>'

def soldier(x, y, s, col=SIL, hat="slouch", rifle=True, flip=False, pose="stand"):
    sx = -s if flip else s
    g = f'<g transform="translate({x} {y}) scale({sx} {s})">'
    if pose == "kneel":
        g += (f'<path d="M-40 0 L -40 -60 L 30 -70 L 40 -10 L 70 -10 L 70 0 Z" fill="{col}"/>'
              f'<path d="M-45 -60 L -50 -180 L 30 -185 L 35 -70 Z" fill="{col}"/>'
              f'<path d="M20 -160 L 110 -120 L 105 -100 L 15 -135 Z" fill="{col}"/>')
        hy = -215
    else:
        g += (f'<rect x="-30" y="-150" width="24" height="150" fill="{col}"/><rect x="4" y="-150" width="24" height="150" fill="{col}"/>'
              f'<path d="M-40 -150 L -44 -280 L 40 -280 L 36 -150 Z" fill="{col}"/>'
              f'<rect x="-58" y="-276" width="20" height="120" rx="8" fill="{col}"/><rect x="38" y="-276" width="20" height="120" rx="8" fill="{col}"/>')
        hy = -310
        if rifle:
            g += f'<path d="M50 -170 L 66 -360 L 74 -360 L 62 -150 Z" fill="{col}"/>'
    g += f'<circle cx="0" cy="{hy}" r="28" fill="{col}"/>'
    if hat == "slouch":
        g += (f'<ellipse cx="0" cy="{hy-18}" rx="60" ry="10" fill="{col}"/><path d="M-26 {hy-20} L -22 {hy-52} L 24 {hy-52} L 28 {hy-20} Z" fill="{col}"/>'
              f'<path d="M-60 {hy-18} L -46 {hy-58} L -30 {hy-22} Z" fill="{col}"/>')
    elif hat == "helmet":
        g += f'<ellipse cx="0" cy="{hy-16}" rx="54" ry="12" fill="{col}"/><path d="M-34 {hy-18} C -30 {hy-60}, 30 {hy-60}, 34 {hy-18} Z" fill="{col}"/>'
    return g + '</g>'

def lewis(x, y, s, col=SIL, flip=False):
    """Lewis gun on bipod, muzzle pointing right; returns svg. Muzzle at (x+210s, y-62s)."""
    sx = -s if flip else s
    return (f'<g transform="translate({x} {y}) scale({sx} {s})">'
            f'<rect x="-40" y="-80" width="200" height="36" rx="14" fill="{col}"/><rect x="160" y="-68" width="50" height="12" fill="{col}"/>'
            f'<rect x="-10" y="-104" width="110" height="20" rx="8" fill="{col}"/>'
            f'<path d="M-40 -74 L -130 -62 L -140 -40 L -40 -50 Z" fill="{col}"/>'
            f'<path d="M120 -50 L 90 0 M120 -50 L 150 0" stroke="{col}" stroke-width="8"/></g>')

def truck(x, y, s, col=SIL, gun=True):
    """1930s flatbed truck facing right, wheels on ground at y."""
    g = f'<g transform="translate({x} {y}) scale({s})">'
    g += (f'<path d="M-300 -70 L -300 -130 L 60 -130 L 60 -70 Z" fill="{col}"/>'
          f'<path d="M60 -70 L 60 -230 L 170 -230 L 190 -150 L 300 -140 L 310 -70 Z" fill="{col}"/>'
          f'<rect x="80" y="-215" width="70" height="55" fill="#C9A04A" opacity="0.35"/>'
          f'<path d="M140 -70 C 150 -120, 240 -120, 260 -70 Z M-240 -70 C -230 -120, -140 -120, -130 -70 Z" fill="{col}"/>')
    for wx in (200, -185):
        g += f'<circle cx="{wx}" cy="-45" r="46" fill="{col}"/><circle cx="{wx}" cy="-45" r="16" fill="#5A4630"/>'
    if gun:
        g += soldier(-120, -130, 0.55, col=col, rifle=False) + lewis(-90, -190, 0.7, col=col)
    return g + '</g>'

def windmill_tower(x, y, s, col=SIL):
    g = f'<g transform="translate({x} {y}) scale({s})">'
    g += f'<path d="M-70 0 L -12 -420 L 12 -420 L 70 0" stroke="{col}" stroke-width="10" fill="none"/>'
    for yy in range(-60, -420, -70):
        w = 70 * (1 + yy / 420)
        g += f'<path d="M{-w-10} {yy} L {w+10} {yy-70} M{w+10} {yy} L {-w-10} {yy-70}" stroke="{col}" stroke-width="5"/>'
    g += f'<path d="M0 -430 L 120 -440 L 150 -470 L 140 -420 Z" fill="{col}"/>'
    return g + '</g>'

def windmill_fan(r=130, col=SIL):
    blades = "".join(f'<path d="M0 0 L {r*math.cos(math.radians(a-6)):.0f} {r*math.sin(math.radians(a-6)):.0f} L {r*math.cos(math.radians(a+6)):.0f} {r*math.sin(math.radians(a+6)):.0f} Z" fill="{col}"/>' for a in range(0, 360, 20))
    return f'<g transform="translate({r+10} {r+10})"><circle r="{r}" fill="none" stroke="{col}" stroke-width="8"/>{blades}<circle r="18" fill="{col}"/></g>'

def homestead(x, y, s, col=SIL):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-220" y="-170" width="440" height="170" fill="{col}"/>'
            f'<path d="M-260 -160 L 0 -300 L 260 -160 Z" fill="{col}"/><path d="M-290 -110 L 290 -110 L 290 -96 L -290 -96 Z" fill="{col}"/>'
            + "".join(f'<rect x="{px}" y="-110" width="10" height="110" fill="{col}"/>' for px in (-285, -140, 0, 140, 275))
            + f'<rect x="-120" y="-80" width="60" height="50" fill="#FFD98A" opacity="0.55"/><rect x="80" y="-80" width="60" height="50" fill="#FFD98A" opacity="0.55"/>'
            f'<rect x="150" y="-330" width="30" height="80" fill="{col}"/></g>')

def fence(y, x0, x1, step=150, col=SIL, gap=None, h=110, sw=4):
    out = ""
    for x in range(x0, x1, step):
        if gap and gap[0] < x < gap[1]:
            out += f'<path d="M{x} {y} L {x+30} {y-h*0.6}" stroke="{col}" stroke-width="12"/>'
            continue
        out += f'<rect x="{x-6}" y="{y-h}" width="12" height="{h}" fill="{col}"/>'
    for k in (0.3, 0.6, 0.9):
        if gap:
            out += f'<path d="M{x0} {y-h*k} L {gap[0]} {y-h*k+8}" stroke="{col}" stroke-width="{sw}"/><path d="M{gap[1]} {y-h*k+10} L {x1} {y-h*k}" stroke="{col}" stroke-width="{sw}"/>'
            out += f'<path d="M{gap[0]} {y-h*k+8} q 30 40 60 60" stroke="{col}" stroke-width="{sw}" fill="none"/>'
        else:
            out += f'<path d="M{x0} {y-h*k} L {x1} {y-h*k}" stroke="{col}" stroke-width="{sw}"/>'
    return out

def rabbit(x, y, s, col=SIL):
    return (f'<g transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="-30" rx="40" ry="28" fill="{col}"/><circle cx="34" cy="-52" r="18" fill="{col}"/>'
            f'<path d="M36 -66 L 40 -110 L 50 -66 Z M28 -66 L 22 -108 L 38 -66 Z" fill="{col}"/><circle cx="-40" cy="-34" r="10" fill="{col}"/></g>')

def kangaroo(x, y, s, col=SIL, flip=False):
    """standing kangaroo, facing right (flip=True faces left), feet on y"""
    sx = -s if flip else s
    return (f'<g transform="translate({x} {y}) scale({sx} {s})">'
            f'<path d="M-40 -90 C -110 -50, -190 -18, -300 -4 L -296 6 C -180 0, -90 -20, -20 -50 Z" fill="{col}"/>'
            f'<ellipse cx="0" cy="-110" rx="72" ry="100" fill="{col}"/>'
            f'<path d="M-30 -30 L -40 0 L 130 0 L 124 -16 L 20 -26 Z" fill="{col}"/>'
            f'<ellipse cx="34" cy="-240" rx="46" ry="95" fill="{col}" transform="rotate(16 34 -240)"/>'
            f'<path d="M50 -300 L 64 -350 L 96 -340 L 80 -290 Z" fill="{col}"/>'
            f'<ellipse cx="88" cy="-362" rx="42" ry="28" fill="{col}" transform="rotate(10 88 -362)"/>'
            f'<ellipse cx="124" cy="-352" rx="30" ry="15" fill="{col}" transform="rotate(14 124 -352)"/>'
            f'<path d="M66 -380 L 56 -440 L 80 -384 Z M84 -384 L 84 -446 L 98 -382 Z" fill="{col}"/>'
            f'<path d="M64 -260 L 104 -222 L 96 -214 L 56 -244 Z" fill="{col}"/></g>')

def wheat_strokes(y0, y1, n, col="#C99A3A", seed=1, op=0.9, hmin=30, hmax=80):
    r = random.Random(seed)
    out = ""
    for _ in range(n):
        x = r.randint(-20, W + 20); y = r.randint(y0, y1)
        f = (y - y0) / max(1, y1 - y0)
        h = hmin + (hmax - hmin) * f
        lean = r.uniform(-8, 8)
        out += f'<path d="M{x} {y} q {lean/2:.0f} {-h/2:.0f} {lean:.0f} {-h:.0f}" stroke="{col}" stroke-width="{2+3*f:.1f}" fill="none" opacity="{op}"/>'
        out += f'<ellipse cx="{x+lean:.0f}" cy="{y-h:.0f}" rx="{2+3*f:.1f}" ry="{6+10*f:.1f}" fill="{col}" opacity="{op}" transform="rotate({lean*2:.0f} {x+lean:.0f} {y-h:.0f})"/>'
    return out
