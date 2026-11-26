import sys
sys.path.insert(0, "ep3")
from art3 import *

DAYSKY = grad("ds", [(0, "#6E9CC4", 1), (1, "#E6E0CC", 1)])
WATER = grad("wa", [(0, "#4A6A80", 1), (1, "#182A36", 1)])
WL = 960  # harbour waterline

# sprites
save("vasa", galleon(560, 840, 1.0), w=1120, h=960)            # waterline at (560, 840) in sprite
save("vasa_closed", galleon(560, 840, 1.0, ports_open=False), w=1120, h=960)
save("stern", f'<g transform="translate(250 820)">{stern_view()}</g>', w=500, h=900)  # waterline (250,820)
save("smoke", '<circle cx="150" cy="150" r="110" fill="#E8E4DC" opacity="0.8" filter="url(#b20)"/>', w=300, h=300)
save("bubble", '<circle cx="20" cy="20" r="12" fill="none" stroke="#B8E0E8" stroke-width="3" opacity="0.8"/>', w=40, h=40)
save("desk", '<rect width="2400" height="1350" fill="url(#dk2)"/>', defs='<radialGradient id="dk2" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3B2A1C"/><stop offset="1" stop-color="#120C08"/></radialGradient>')
save("hull_rise", galleon(560, 840, 1.0, sails=False, flags=False, col="#2A2018", ports_open=False), w=1120, h=960)
save("fish", '<path d="M10 30 C 40 0, 90 0, 110 30 C 90 60, 40 60, 10 30 Z M10 30 L -10 10 L -10 50 Z" fill="#2A4A50"/>', w=130, h=60)

# ---------- harbour (Stockholm 1628) ----------
save("harbour_back", f'<rect width="{W}" height="{H}" fill="url(#ds)"/>'
     + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="50" fill="#F4F0E4" opacity="0.6" filter="url(#b40)"/>' for x, y, rx in [(400, 200, 300), (1300, 140, 380), (2000, 260, 320)])
     + skyline(800, "#4A4A5A", 3) + f'<rect y="800" width="{W}" height="20" fill="#3A3A48"/>'
     + crowd(820, 0, 1100, "#2A2430", 4, 1.0) + crowd(820, 1500, 2400, "#2A2430", 5, 1.0)
     + f'<rect y="820" width="{W}" height="{H-820}" fill="url(#wa)"/>' + waves(840, H, "#D8E4EA", 0.18, 36),
     defs=DAYSKY + WATER + BLUR)
save("harbour_front", f'<rect y="{WL}" width="{W}" height="{H-WL}" fill="url(#wf)"/>' + waves(WL + 10, H, "#C8D8E0", 0.25, 44, seed=4)
     + f'<path d="M0 {H} L 0 1150 C 200 1120, 380 1160, 520 {H} Z" fill="#2A2A22"/>' + crowd(1170, 0, 420, "#141014", 6, 1.8),
     defs=grad("wf", [(0, "#3E5E74", 0.97), (1, "#14222C", 1)]))

# ---------- sinking (same harbour, darker gusty sky) ----------
save("sinking_back", f'<rect width="{W}" height="{H}" fill="url(#gs)"/>'
     + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="60" fill="#8A929A" opacity="0.5" filter="url(#b40)"/>' for x, y, rx in [(300, 220, 360), (1200, 160, 420), (2050, 280, 380)])
     + skyline(800, "#3A3E4A", 7) + crowd(820, 200, 2200, "#22202A", 8, 1.0)
     + f'<rect y="820" width="{W}" height="{H-820}" fill="url(#wa)"/>' + waves(840, H, "#D8E4EA", 0.2, 30),
     defs=grad("gs", [(0, "#5A6A7A", 1), (1, "#C8CCCC", 1)]) + WATER + BLUR)

# ---------- king ----------
save("king_back", f'<rect width="{W}" height="{H}" fill="url(#kg)"/><circle cx="1200" cy="560" r="420" fill="#E8C88A" opacity="0.35" filter="url(#b40)"/>'
     + f'<path d="M0 1100 L 2400 1100 L 2400 {H} L 0 {H} Z" fill="#1A1418"/>'
     + "".join(f'<rect x="{x}" y="300" width="16" height="800" fill="#1A1418"/><path d="M{x+16} 310 L {x+190} 340 L {x+16} 380 Z" fill="#2B5DA8"/><path d="M{x+16} 336 L {x+150} 346 L {x+16} 356 Z" fill="#E8C040"/>' for x in (400, 1830)),
     defs=grad("kg", [(0, "#2A1E28", 1), (1, "#7A4A3A", 1)]) + BLUR)
save("king_front", figure17(1200, 1110, 1.6))

# ---------- navy (storm, Bay of Riga) ----------
save("navy_back", f'<rect width="{W}" height="{H}" fill="url(#st)"/>' + fog(200, 600, 10, col="#2A2E34", op=(0.4, 0.6))
     + f'<rect y="820" width="{W}" height="{H-820}" fill="#1E2A30"/>' + waves(830, H, "#AAB8C0", 0.3, 30)
     + "".join(f'<g transform="rotate({r} {x} 830)">{galleon(x, 830, s, col="#141414", sails=False, flags=False, sil=True)}</g>' for x, s, r in [(500, 0.5, -24), (1300, 0.4, 30), (2000, 0.55, -12)]),
     defs=grad("st", [(0, "#1A1E26", 1), (1, "#4A525A", 1)]))
save("navy_front", f'<path d="M0 {H} L 0 1000 Q 300 900, 600 1000 T 1200 1000 T 1800 1000 T 2400 1000 L 2400 {H} Z" fill="#141E24"/>')

# ---------- shipyard ----------
scaff = "".join(f'<rect x="{x}" y="420" width="12" height="520" fill="#2A1E16"/>' for x in range(620, 1820, 120))
scaff += "".join(f'<rect x="600" y="{y}" width="1240" height="10" fill="#2A1E16"/>' for y in (520, 640, 760))
save("shipyard_back", f'<rect width="{W}" height="{H}" fill="url(#ds)"/>' + skyline(760, "#6A6A78", 9)
     + f'<rect y="760" width="{W}" height="{H-760}" fill="#5A4A3A"/>' + f'<path d="M500 960 L 1900 900 L 1900 960 Z" fill="#3A2A1E"/>',
     defs=DAYSKY)
save("shipyard_front", galleon(1220, 930, 1.6, sails=False, flags=False, ports_open=False) + scaff
     + f'<path d="M2050 940 L 2080 300 L 2110 940 Z" fill="#2A1E16"/><path d="M2080 320 L 1800 380" stroke="#2A1E16" stroke-width="12"/><path d="M1810 380 L 1810 600" stroke="#2A1E16" stroke-width="3"/>'
     + "".join(worker(x, 1020, 1.1, pose=i % 2) for i, x in enumerate((300, 520, 1950, 2200)))
     + f'<rect y="1020" width="{W}" height="{H-1020}" fill="#3A2A1E"/>')

# ---------- plans (parchment cross-section) ----------
pl = (f'<rect width="{W}" height="{H}" fill="#E6D6B2"/>'
      + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#8A7350" stroke-width="2" opacity="0.2"/>' for x in range(0, W + 1, 100))
      + f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="#5A4630" stroke-width="6"/>'
      + f'<g transform="translate(1200 820)"><path d="M-420 120 C -460 0, -480 -260, -440 -420 L 440 -420 C 480 -260, 460 0, 420 120 C 300 260, -300 260, -420 120 Z" fill="none" stroke="#3A2A1E" stroke-width="10"/>'
      + f'<line x1="-470" y1="-100" x2="470" y2="-100" stroke="#3A2A1E" stroke-width="6"/><line x1="-460" y1="-260" x2="460" y2="-260" stroke="#3A2A1E" stroke-width="6"/>'
      + f'<line x1="-600" y1="80" x2="600" y2="80" stroke="#2B5DA8" stroke-width="6" stroke-dasharray="20 14"/>'
      + "".join(f'<rect x="{gx}" y="{gy}" width="110" height="34" rx="12" fill="#3A2A1E"/>' for gx in (-420, 310) for gy in (-150, -310))
      + '</g>'
      f'<text x="1200" y="1010" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="40" fill="#2B5DA8" text-anchor="middle">waterline</text>'
      f'<text x="1780" y="530" font-family="Playfair Display SC" font-weight="900" font-size="44" fill="#3A2A1E">UPPER GUN DECK</text>'
      f'<text x="1780" y="690" font-family="Playfair Display SC" font-weight="900" font-size="44" fill="#3A2A1E">LOWER GUN DECK</text>'
      f'<text x="1200" y="180" font-family="Playfair Display SC" font-weight="900" font-size="64" fill="#3A2A1E" text-anchor="middle">VASA · CROSS-SECTION</text>'
      f'<text x="{W-90}" y="{H-80}" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="34" fill="#5A4630" text-anchor="end">simplified diagram</text>')
save("plans_back", pl)
save("plans_front", "")

# ---------- carvings (stern close-up, gilded) ----------
carv = "".join(f'<g transform="translate({x} {y})"><circle r="{r}" fill="#C9A04A"/><circle r="{r*0.55}" fill="#8A2A1E"/><circle cx="-{r*0.25:.0f}" cy="-{r*0.2:.0f}" r="{r*0.12:.0f}" fill="#E8C878"/></g>'
               for x, y, r in [(900, 500, 60), (1200, 470, 70), (1500, 500, 60), (1050, 700, 50), (1350, 700, 50), (1200, 880, 64)])
save("carvings_back", f'<rect width="{W}" height="{H}" fill="#2A1A12"/>'
     + f'<path d="M700 1350 L 720 300 C 900 220, 1500 220, 1680 300 L 1700 1350 Z" fill="#3A2216"/>'
     + f'<path d="M720 300 C 900 220, 1500 220, 1680 300" stroke="#C9A04A" stroke-width="18" fill="none"/>' + carv
     + "".join(f'<path d="M{x} 380 C {x-30} 600, {x+30} 900, {x} 1300" stroke="#C9A04A" stroke-width="14" fill="none"/>' for x in (780, 1620))
     + "".join(f'<rect x="{x}" y="1000" width="90" height="120" fill="#8A2A1E"/>' for x in (860, 1040, 1270, 1450)))
save("carvings_front", "")

# ---------- test (stern view on calm water by the quay) ----------
save("test_back", f'<rect width="{W}" height="{H}" fill="url(#ds)"/>' + skyline(800, "#6A6A7A", 10)
     + f'<rect y="800" width="{W}" height="{H-800}" fill="url(#wa)"/>' + waves(820, H, "#D8E4EA", 0.18, 36), defs=DAYSKY + WATER)
save("test_front", f'<rect y="1000" width="{W}" height="{H-1000}" fill="url(#wf)"/>' + waves(1010, H, "#C8D8E0", 0.25, 44),
     defs=grad("wf", [(0, "#3E5E74", 0.92), (1, "#14222C", 1)]))

# ---------- inquiry (old document on desk) ----------
PW, PH = 1150, 1500
r = random.Random(31)
lines = ""
y = 560
while y < PH - 120:
    lines += f'<rect x="110" y="{y}" width="{r.choice([930, 930, 880, 820, 600])}" height="10" rx="5" fill="#3A3226" opacity="0.5"/>'
    y += 34
save("inquiry", f'<rect width="{PW}" height="{PH}" fill="#E2D0A6"/><rect x="30" y="30" width="{PW-60}" height="{PH-60}" fill="none" stroke="#5A4630" stroke-width="4"/>'
     f'<text x="{PW/2}" y="200" font-family="Playfair Display" font-style="italic" font-weight="900" font-size="84" fill="#2A1E14" text-anchor="middle">Protocol of the Inquest</text>'
     f'<text x="{PW/2}" y="290" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="46" fill="#2A1E14" text-anchor="middle">concerning the loss of the ship Vasa</text>'
     f'<text x="{PW/2}" y="370" font-family="Playfair Display SC" font-weight="900" font-size="40" fill="#5A4630" text-anchor="middle">STOCKHOLM · SEPTEMBER 1628</text>'
     f'<line x1="200" y1="420" x2="{PW-200}" y2="420" stroke="#5A4630" stroke-width="3"/>{lines}'
     f'<circle cx="{PW-220}" cy="{PH-200}" r="80" fill="#8A2A1E" opacity="0.9"/>', w=PW, h=PH)

# ---------- underwater ----------
rays = "".join(f'<polygon points="{x},0 {x+80},0 {x+300},{H} {x+120},{H}" fill="#9AD0D0" opacity="0.07"/>' for x in range(0, W, 340))
save("underwater_back", f'<rect width="{W}" height="{H}" fill="url(#uw)"/>{rays}'
     + f'<path d="M0 1080 C 400 1040, 900 1070, 1400 1050 C 1800 1035, 2100 1060, 2400 1050 L 2400 {H} L 0 {H} Z" fill="#2A3A32"/>',
     defs=grad("uw", [(0, "#2A6A72", 1), (1, "#081A1E", 1)]))
save("underwater_front", f'<g transform="rotate(-6 1200 1060)">{galleon(1200, 1030, 1.25, sails=False, flags=False, col="#1A2420", ports_open=False)}</g>'
     + f'<rect x="1090" y="300" width="14" height="700" fill="#1A2420" transform="rotate(-6 1200 1060)"/>'
     + f'<path d="M0 1120 C 500 1080, 1000 1110, 1500 1100 C 1900 1090, 2200 1110, 2400 1100 L 2400 {H} L 0 {H} Z" fill="#1E2C26"/>'
     + fog(700, 1100, 8, col="#3A6A6A", op=(0.15, 0.3)))

# ---------- raising (1961, pontoons; hull animated) ----------
save("raising_back", f'<rect width="{W}" height="{H}" fill="url(#rs)"/><rect y="420" width="{W}" height="{H-420}" fill="url(#ru)"/>'
     + "".join(f'<rect x="{x}" y="360" width="420" height="80" rx="16" fill="#3A3A3A"/>' for x in (450, 1530))
     + f'<path d="M0 420 q 60 -14 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0 t 120 0" stroke="#C8E0E8" stroke-width="5" fill="none"/>',
     defs=grad("rs", [(0, "#8AB0CC", 1), (1, "#D8E4EA", 1)]) + grad("ru", [(0, "#2E5A66", 1), (1, "#081418", 1)]))
save("raising_front", f'<rect y="420" width="{W}" height="{H-420}" fill="#2E5A66" opacity="0.38"/>' + fog(600, 1300, 8, col="#3A6A6A", op=(0.15, 0.25)))

# ---------- museum ----------
save("museum_back", f'<rect width="{W}" height="{H}" fill="#0C0E12"/>'
     + "".join(f'<polygon points="{x},0 {x+60},0 {x+260},{H} {x-140},{H}" fill="#FFE8B8" opacity="0.06"/>' for x in (500, 1150, 1800))
     + f'<rect y="1120" width="{W}" height="{H-1120}" fill="#16181C"/>'
     + galleon(1200, 1000, 1.35, sails=False, flags=False, ports_open=False, col="#4A2E1E")
     + "".join(f'<rect x="{x}" y="{1000-1.35*152-560}" width="14" height="560" fill="#3A2418"/>' for x in (1200 + 200 * 1.35 - 7, 1200 + 20 * 1.35 - 7, 1200 - 200 * 1.35 - 7)))
save("museum_front", crowd(1250, 200, 900, "#050608", 11, 4.0) + crowd(1250, 1500, 2300, "#050608", 12, 4.0))
print("ep3 scenes done")
