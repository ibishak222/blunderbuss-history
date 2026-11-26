"""Episode 3 (Vasa) drawing helpers. Canvas 2400x1350."""
import sys, random, math, os
sys.path.insert(0, "long")
import art
from art import *
art.OUT = "ep3/layers/"
os.makedirs(art.OUT, exist_ok=True)

HULL, GOLD_, SAIL = "#3A2216", "#C9A04A", "#E8DCC0"

def galleon(x, y, s, col=HULL, sails=True, ports_open=True, sil=False, flags=True):
    """17th-century two-deck warship, bow to the right, waterline at (x, y)."""
    c = col
    g = f'<g transform="translate({x} {y}) scale({s})">'
    hull = ('M -330 40 C -200 85, 200 85, 300 20 L 335 -110 L 395 -128 L 388 -142 L 300 -152 L 160 -152 '
            'L -120 -162 L -240 -178 L -258 -248 L -352 -256 L -346 -100 Z')
    sc = SAIL if not sil else col
    if sails:
        def sq(cx, top, w, h, curve=18):
            return f'<path d="M{cx-w/2} {top} L {cx+w/2} {top} Q {cx+w/2+curve} {top+h/2}, {cx+w/2-4} {top+h} L {cx-w/2+4} {top+h} Q {cx-w/2+curve} {top+h/2}, {cx-w/2} {top} Z" fill="{sc}" stroke="{col}" stroke-width="3"/>'
        # masts
        for mx, mh in ((200, 560), (20, 640), (-200, 460)):
            g += f'<rect x="{mx-6}" y="{-152-mh}" width="12" height="{mh}" fill="{col}"/>'
        g += f'<path d="M330 -150 L 500 -290" stroke="{col}" stroke-width="10"/>'
        g += sq(20, -560, 250, 190) + sq(20, -330, 300, 150) + sq(200, -500, 210, 170) + sq(200, -300, 250, 130)
        g += sq(20, -720, 160, 130) + sq(200, -640, 140, 110)
        g += f'<path d="M-200 -560 L -200 -230 L -60 -250 Z" fill="{sc}" stroke="{col}" stroke-width="3"/>'
        g += f'<path d="M400 -230 L 520 -230 L 515 -175 L 405 -175 Z" fill="{sc}" stroke="{col}" stroke-width="3"/>'
        for mx, mh in ((200, 560), (20, 640), (-200, 460)):
            g += f'<rect x="{mx-120}" y="{-152-mh+40}" width="240" height="6" fill="{col}"/>' if mx != -200 else ""
        if flags:
            g += (f'<path d="M20 -792 L 120 -775 L 20 -760 Z" fill="#2B5DA8"/><path d="M200 -712 L 280 -700 L 200 -688 Z" fill="#E8C040"/>'
                  f'<path d="M-200 -612 L -130 -602 L -200 -592 Z" fill="#2B5DA8"/>')
    g += f'<path d="{hull}" fill="{col}"/>'
    if not sil:
        g += f'<path d="M -346 -100 L -240 -178 L -120 -162 L 160 -152 L 300 -152 L 388 -142" stroke="{GOLD_}" stroke-width="6" fill="none"/>'
        g += f'<path d="M -330 -20 C -200 -2, 200 -4, 310 -30" stroke="{GOLD_}" stroke-width="4" fill="none" opacity="0.8"/>'
        pc = "#B8402A" if ports_open else "#1A0E08"
        for row, yy in ((0, -58), (1, -108)):
            for px in range(-230, 260, 44):
                g += f'<rect x="{px}" y="{yy}" width="18" height="18" fill="{pc}"/>'
                if ports_open:
                    g += f'<rect x="{px+4}" y="{yy+6}" width="22" height="6" fill="#141414"/>'
        g += "".join(f'<circle cx="{sx}" cy="{sy}" r="9" fill="{GOLD_}"/>' for sx, sy in [(-330, -220), (-300, -230), (-270, -225), (-320, -170), (-290, -180), (-330, -130), (360, -134), (380, -138)])
    return g + '</g>'

def stern_view(col=HULL):
    """end-on hull for the stability test; waterline at y=0, centred at x=0"""
    return (f'<path d="M-150 60 C -170 0, -180 -120, -160 -220 L 160 -220 C 180 -120, 170 0, 150 60 Z" fill="{col}"/>'
            f'<path d="M-130 -220 L -120 -330 L 120 -330 L 130 -220 Z" fill="{col}"/>'
            f'<rect x="-8" y="-760" width="16" height="560" fill="{col}"/>'
            f'<rect x="-170" y="-640" width="340" height="10" fill="{col}"/><rect x="-140" y="-480" width="280" height="10" fill="{col}"/>'
            f'<path d="M-160 -220 L 160 -220" stroke="{GOLD_}" stroke-width="5"/>'
            + "".join(f'<rect x="{px}" y="{py}" width="16" height="16" fill="#B8402A"/>' for px in (-150, 134) for py in (-80, -140)))

def skyline(y, col="#2A2A3A", seed=1):
    r = random.Random(seed)
    out = ""
    x = 0
    while x < W:
        w = r.randint(40, 90); h = r.randint(60, 150)
        out += f'<path d="M{x} {y} L {x} {y-h} L {x+w/2} {y-h-r.randint(20,60)} L {x+w} {y-h} L {x+w} {y} Z" fill="{col}"/>'
        x += w + r.randint(0, 10)
    # churches and the castle tower
    for cx, h in ((420, 340), (980, 300), (1500, 420), (1900, 280)):
        out += f'<rect x="{cx-30}" y="{y-h}" width="60" height="{h}" fill="{col}"/><path d="M{cx-34} {y-h} L {cx} {y-h-140} L {cx+34} {y-h} Z" fill="{col}"/>'
    return out

def crowd(y, x0, x1, col="#1A1418", seed=2, scale=1.0):
    r = random.Random(seed)
    out = ""
    for x in range(x0, x1, int(14 * scale)):
        h = r.randint(26, 40) * scale
        out += f'<rect x="{x}" y="{y-h}" width="{9*scale:.0f}" height="{h:.0f}" fill="{col}"/><circle cx="{x+4.5*scale:.0f}" cy="{y-h-6*scale:.0f}" r="{6*scale:.0f}" fill="{col}"/>'
    return out

def figure17(x, y, s, col="#1A1418"):
    """17th-century king figure: wide plumed hat, cloak, sword"""
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-90 0 L -70 -260 C -60 -300, 60 -300, 70 -260 L 90 0 Z" fill="{col}"/>'
            f'<path d="M-110 -250 C -90 -320, 90 -320, 110 -250 L 60 -230 L -60 -230 Z" fill="{col}"/>'
            f'<circle cx="0" cy="-340" r="40" fill="{col}"/><path d="M-30 -312 C -10 -280, 10 -280, 30 -312 L 20 -290 L -20 -290 Z" fill="{col}"/>'
            f'<ellipse cx="0" cy="-372" rx="90" ry="16" fill="{col}"/><path d="M-40 -380 C -36 -420, 36 -420, 40 -380 Z" fill="{col}"/>'
            f'<path d="M30 -400 C 90 -440, 140 -420, 150 -380 C 110 -400, 70 -400, 40 -385 Z" fill="{col}"/>'
            f'<path d="M60 -120 L 160 -20" stroke="{col}" stroke-width="10"/></g>')

def worker(x, y, s, col="#1A1418", pose=0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-14" y="-90" width="12" height="90" fill="{col}"/><rect x="4" y="-90" width="12" height="90" fill="{col}"/>'
            f'<rect x="-20" y="-170" width="40" height="84" fill="{col}"/><circle cx="0" cy="-188" r="18" fill="{col}"/>'
            + (f'<path d="M18 -160 L 60 -210 L 66 -204 L 24 -150 Z" fill="{col}"/><rect x="50" y="-232" width="40" height="18" fill="{col}"/>' if pose else
               f'<path d="M-20 -160 L -50 -100 M20 -160 L 50 -100" stroke="{col}" stroke-width="12"/>') + '</g>')

def diver(x, y, s, col="#0E1A20"):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="-200" r="46" fill="{col}"/><circle cx="0" cy="-200" r="20" fill="#5A8A90" opacity="0.6"/>'
            f'<rect x="-50" y="-160" width="100" height="120" rx="20" fill="{col}"/><rect x="-46" y="-40" width="36" height="110" fill="{col}"/><rect x="10" y="-40" width="36" height="110" fill="{col}"/>'
            f'<path d="M-50 -140 L -110 -90 M50 -140 L 110 -100" stroke="{col}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M0 -246 C 0 -400, 60 -600, 40 -900" stroke="{col}" stroke-width="6" fill="none"/></g>')
