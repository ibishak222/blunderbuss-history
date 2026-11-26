import sys, random, math, os
sys.path.insert(0, "long")
import art
from art import *
art.OUT = "ep5/layers/"
os.makedirs(art.OUT, exist_ok=True)

def starfield(n=500, seed=1):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(0,H)}" r="{r.choice([1,1.5,2,2.5,3])}" fill="#FFFFFF" opacity="{r.uniform(0.2,0.9):.2f}"/>' for _ in range(n))

SPACE = '<radialGradient id="neb" cx="30%" cy="30%" r="70%"><stop offset="0" stop-color="#2A1E4A"/><stop offset="0.6" stop-color="#0C0E1E"/><stop offset="1" stop-color="#05060C"/></radialGradient>'
MARS = ('<radialGradient id="mars" cx="35%" cy="35%" r="70%"><stop offset="0" stop-color="#E88A5A"/><stop offset="0.55" stop-color="#B5502E"/><stop offset="1" stop-color="#3A120A"/></radialGradient>'
        '<radialGradient id="atm" cx="50%" cy="50%" r="50%"><stop offset="0.9" stop-color="#FFB080" stop-opacity="0"/><stop offset="0.97" stop-color="#FFB080" stop-opacity="0.5"/><stop offset="1" stop-color="#FFB080" stop-opacity="0"/></radialGradient>')

def mars(cx, cy, r, seed=3):
    rr = random.Random(seed)
    craters = "".join(f'<ellipse cx="{cx + rr.uniform(-0.7,0.7)*r:.0f}" cy="{cy + rr.uniform(-0.7,0.7)*r:.0f}" rx="{rr.uniform(0.03,0.09)*r:.0f}" ry="{rr.uniform(0.02,0.06)*r:.0f}" fill="#8A3A22" opacity="0.5"/>' for _ in range(30))
    return (f'<circle cx="{cx}" cy="{cy}" r="{r*1.06:.0f}" fill="url(#atm)"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#mars)"/>{craters}'
            f'<ellipse cx="{cx-0.1*r:.0f}" cy="{cy-0.86*r:.0f}" rx="{0.3*r:.0f}" ry="{0.08*r:.0f}" fill="#F4E8E0" opacity="0.8"/>'
            f'<path d="M{cx-r*0.9:.0f} {cy-r*0.1:.0f} C {cx-r*0.3:.0f} {cy:.0f}, {cx+r*0.3:.0f} {cy-r*0.2:.0f}, {cx+r*0.9:.0f} {cy-r*0.05:.0f}" stroke="#7A2A18" stroke-width="{r*0.05:.0f}" fill="none" opacity="0.5"/>')

def orbiter(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<rect x="-50" y="-60" width="100" height="120" fill="#C8B070"/><rect x="-50" y="-60" width="100" height="120" fill="none" stroke="#6A5A30" stroke-width="4"/>'
            f'<rect x="50" y="-8" width="40" height="16" fill="#8A8A8A"/>'
            + "".join(f'<rect x="{90 + i*70}" y="-50" width="66" height="100" fill="#1E3A7A" stroke="#8AA0D0" stroke-width="3"/>' for i in range(3))
            + f'<ellipse cx="-50" cy="0" rx="18" ry="70" fill="#E8E8E8"/><path d="M-50 0 L -90 0" stroke="#8A8A8A" stroke-width="5"/>'
            f'<path d="M-20 60 L 20 60 L 30 100 L -30 100 Z" fill="#5A5A5A"/></g>')

# ---------- sprites ----------
save("orbiter", orbiter(260, 160, 1.0), w=520, h=300)        # centre (260,160)
save("flame", '<path d="M150 10 C 190 80, 180 180, 150 290 C 120 180, 110 80, 150 10 Z" fill="url(#fg)"/>', w=300, h=300,
     defs='<linearGradient id="fg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.4" stop-color="#FFC060"/><stop offset="1" stop-color="#FF6020" stop-opacity="0"/></linearGradient>')
save("rocket", '<rect x="70" y="80" width="60" height="700" fill="#F2F2F2"/><path d="M70 80 L 100 0 L 130 80 Z" fill="#F2F2F2"/>'
     + "".join(f'<rect x="{x}" y="600" width="24" height="180" rx="10" fill="#E8E8E8"/>' for x in (40, 136))
     + '<rect x="70" y="300" width="60" height="30" fill="#2B5DA8"/><rect x="70" y="760" width="60" height="20" fill="#3A3A3A"/>', w=200, h=800)
save("plume", '<ellipse cx="200" cy="200" rx="180" ry="120" fill="#F0EAE0" opacity="0.8" filter="url(#b20)"/>', w=400, h=400)
save("desk", '<rect width="2400" height="1350" fill="url(#dk2)"/>', defs='<radialGradient id="dk2" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#2A2E3A"/><stop offset="1" stop-color="#0A0C12"/></radialGradient>')

# ---------- mars (orbiter near the planet) ----------
save("mars_back", f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(500, 2)}{mars(1500, 700, 560)}', defs=SPACE + MARS)
save("mars_front", "")
# ---------- arrival (big Mars at right edge; orbiter animated) ----------
save("arrival_back", f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(500, 4)}', defs=SPACE)
save("arrival_planet", f'{mars(1900, 760, 760, 5)}', defs=MARS)
save("arrival_front", "")
# ---------- orbiter close-up ----------
save("orbiter_back", f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(600, 6)}<circle cx="300" cy="250" r="60" fill="#FFF4D0"/><circle cx="300" cy="250" r="200" fill="#FFF4D0" opacity="0.08"/>', defs=SPACE)
save("orbiter_front", orbiter(1200, 680, 3.2))
# ---------- cruise (solar system diagram) ----------
cru = (f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(400, 7)}'
       f'<circle cx="1200" cy="675" r="70" fill="#FFE08A"/><circle cx="1200" cy="675" r="160" fill="#FFE08A" opacity="0.12"/>'
       f'<ellipse cx="1200" cy="675" rx="380" ry="300" fill="none" stroke="#4A7AC0" stroke-width="3" stroke-dasharray="10 10"/>'
       f'<ellipse cx="1200" cy="675" rx="620" ry="470" fill="none" stroke="#C0603A" stroke-width="3" stroke-dasharray="10 10"/>'
       f'<text x="1200" y="1270" font-family="Montserrat" font-weight="700" font-size="34" fill="#8A92A8" text-anchor="middle">simplified, not to scale</text>')
save("cruise_back", cru, defs=SPACE)
save("cruise_front", "")
# ---------- control room ----------
screens = ""
for i, x in enumerate(range(260, 2300, 420)):
    screens += f'<rect x="{x}" y="520" width="300" height="200" rx="10" fill="#0E1A14"/><rect x="{x+12}" y="532" width="276" height="176" fill="#1E5A3A" opacity="0.9"/>'
    screens += "".join(f'<rect x="{x+30}" y="{550 + j*26}" width="{random.Random(i*10+j).randint(80, 230)}" height="10" fill="#7AF0A8" opacity="0.7"/>' for j in range(6))
save("control_back", f'<rect width="{W}" height="{H}" fill="#0A0C12"/><rect x="200" y="120" width="2000" height="340" fill="#121A2A"/>'
     + f'<circle cx="900" cy="290" r="130" fill="#B5502E"/><path d="M 1050 290 C 1300 200, 1600 220, 1900 300" stroke="#7AF0A8" stroke-width="5" fill="none" stroke-dasharray="14 10"/>' + screens
     + f'<rect y="720" width="{W}" height="80" fill="#1A1E28"/><rect y="800" width="{W}" height="220" fill="#232C3E"/>')
people = "".join(f'<g transform="translate({x} 1120) scale(1.4)"><rect x="-34" y="-150" width="68" height="150" rx="20" fill="#020304"/><circle cx="0" cy="-180" r="34" fill="#020304"/></g>' for x in (420, 900, 1450, 1950))
save("control_front", people + f'<rect y="1110" width="{W}" height="{H-1110}" fill="#07080C"/>')
# ---------- launch ----------
save("launch_back", f'<rect width="{W}" height="{H}" fill="url(#ls)"/>' + f'<rect y="1000" width="{W}" height="{H-1000}" fill="#4A5A3A"/><rect y="980" width="{W}" height="24" fill="#2A3A4A"/>'
     + f'<rect x="1300" y="300" width="60" height="700" fill="#5A2A1A"/>' + "".join(f'<rect x="1300" y="{y}" width="170" height="10" fill="#5A2A1A"/>' for y in range(340, 980, 90)),
     defs=grad("ls", [(0, "#5A8AC0", 1), (1, "#E8E4D8", 1)]))
save("launch_front", "")
# ---------- units (chalkboard) ----------
save("units_back", f'<rect width="{W}" height="{H}" fill="#2A3A30"/><rect x="60" y="60" width="{W-120}" height="{H-120}" fill="#1E2C24" stroke="#6A4A2A" stroke-width="30"/>'
     f'<text x="1200" y="300" font-family="Anton" font-size="120" fill="#F0F0E8" text-anchor="middle">1 lbf·s  =  4.45 N·s</text>'
     f'<text x="700" y="500" font-family="Montserrat" font-weight="800" font-size="56" fill="#E8C878" text-anchor="middle">LOCKHEED MARTIN SENT</text>'
     f'<text x="1700" y="500" font-family="Montserrat" font-weight="800" font-size="56" fill="#9AD0F0" text-anchor="middle">JPL EXPECTED</text>'
     f'<text x="700" y="590" font-family="Montserrat" font-weight="700" font-size="48" fill="#E8C878" text-anchor="middle">pound-force seconds</text>'
     f'<text x="1700" y="590" font-family="Montserrat" font-weight="700" font-size="48" fill="#9AD0F0" text-anchor="middle">newton-seconds</text>'
     f'<line x1="1200" y1="430" x2="1200" y2="1150" stroke="#F0F0E8" stroke-width="5" opacity="0.6"/>')
save("units_front", "")
# ---------- trajectory (altitude diagram) ----------
tr = (f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(300, 9)}'
      f'<path d="M-200 1500 A 1800 1800 0 0 1 2600 1500 Z" fill="url(#mars)" transform="translate(0 0)"/>')
save("trajectory_back", f'<rect width="{W}" height="{H}" fill="url(#neb)"/>{starfield(300, 9)}<circle cx="1200" cy="3100" r="2100" fill="url(#mars)"/>'
     f'<circle cx="1200" cy="3100" r="2160" fill="none" stroke="#FFB080" stroke-width="40" opacity="0.15"/>', defs=SPACE + MARS)
save("trajectory_front", "")
# ---------- documents ----------
PW, PH = 1150, 1500
r = random.Random(51); lines = ""; y = 600
while y < PH - 120:
    lines += f'<rect x="110" y="{y}" width="{r.choice([930, 930, 880, 820, 600])}" height="10" rx="5" fill="#3A3A3A" opacity="0.5"/>'; y += 34
save("paper", f'<rect width="{PW}" height="{PH}" fill="#F4F4F0"/><rect x="0" y="0" width="{PW}" height="120" fill="#1E3A7A"/>'
     f'<text x="{PW/2}" y="80" font-family="Montserrat" font-weight="800" font-size="44" fill="#FFFFFF" text-anchor="middle">MARS CLIMATE ORBITER</text>'
     f'<text x="{PW/2}" y="280" font-family="Montserrat" font-weight="800" font-size="64" fill="#1A1A1A" text-anchor="middle">Mishap Investigation</text>'
     f'<text x="{PW/2}" y="360" font-family="Montserrat" font-weight="800" font-size="64" fill="#1A1A1A" text-anchor="middle">Board</text>'
     f'<text x="{PW/2}" y="450" font-family="Montserrat" font-weight="600" font-size="40" fill="#5A5A5A" text-anchor="middle">Phase I Report · November 10, 1999</text>'
     f'<line x1="150" y1="510" x2="{PW-150}" y2="510" stroke="#1E3A7A" stroke-width="4"/>{lines}', w=PW, h=PH)
print("ep5 scenes done")
