import sys
sys.path.insert(0, "ep2")
from art2 import *

SUNSET = grad("ss", [(0, "#2A1E3A", 1), (0.55, "#C8643C", 1), (1, "#F4B860", 1)])
DAY = grad("dy", [(0, "#5E9BC8", 1), (1, "#E8D7A8", 1)])
DUSK = grad("dk", [(0, "#1C2238", 1), (0.6, "#8A4A48", 1), (1, "#E09A5C", 1)])
FIELD = grad("fd", [(0, "#B98A3A", 1), (1, "#6A4A22", 1)])
FIELD_D = grad("fdd", [(0, "#7A5A30", 1), (1, "#2A1C10", 1)])
HZ = 820

def hills(y, col, seed=1, amp=60):
    r = random.Random(seed)
    d = f"M0 {y}"
    for x in range(0, W + 200, 200):
        d += f" Q {x+100} {y - r.randint(10, amp)}, {x+200} {y}"
    return f'<path d="{d} L {W} {H} L 0 {H} Z" fill="{col}"/>'

# ---------- sprites ----------
for pose in ("stand", "peck", "run0", "run1", "run2", "run3"):
    save(f"emu_{pose}", emu(150, 430, 1.0, pose), w=360, h=450)
save("dust", '<ellipse cx="150" cy="200" rx="140" ry="60" fill="#C8A878" opacity="0.7" filter="url(#b20)"/><ellipse cx="120" cy="170" rx="70" ry="50" fill="#D8B888" opacity="0.6" filter="url(#b6)"/>', w=300, h=280)
save("flash", '<circle cx="150" cy="150" r="150" fill="url(#fl)"/>', w=300, h=300,
     defs='<radialGradient id="fl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.3" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="#D9482B" stop-opacity="0"/></radialGradient>')
save("fan", windmill_fan(), w=280, h=280)
save("rabbit", rabbit(60, 120, 1.0), w=140, h=130)
save("truck", truck(330, 420, 1.0), w=680, h=440)
save("desk", '<rect width="2400" height="1350" fill="url(#dk2)"/>', defs='<radialGradient id="dk2" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3B2A1C"/><stop offset="1" stop-color="#120C08"/></radialGradient>')
save("stamp", f'<g transform="rotate(-10 340 140)"><rect x="20" y="20" width="660" height="230" rx="18" fill="none" stroke="{RED}" stroke-width="14"/>'
     f'<text x="350" y="140" font-family="Anton" font-size="104" fill="{RED}" text-anchor="middle">10 ROUNDS</text>'
     f'<text x="350" y="215" font-family="Montserrat" font-weight="800" font-size="46" fill="{RED}" text-anchor="middle" letter-spacing="8">PER BIRD</text></g>', w=720, h=340)

# ---------- emus_field (sunset wheat) ----------
r = random.Random(4)
static_emus = "".join(emu(x, y, s, r.choice(["stand", "peck", "peck"]), flip=r.random() < 0.4) for x, y, s in
                      [(400, 900, 0.5), (620, 880, 0.42), (900, 910, 0.55), (1250, 875, 0.38), (1500, 895, 0.48), (1720, 870, 0.36), (1980, 905, 0.52), (2200, 880, 0.4), (780, 960, 0.7), (1650, 980, 0.75)])
save("emus_field_back", f'<rect width="{W}" height="{H}" fill="url(#ss)"/><circle cx="1650" cy="760" r="170" fill="#FFD98A" opacity="0.9"/>'
     + hills(HZ, "#6A3A2A", 2, 40) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>' + wheat_strokes(HZ + 10, 1000, 900, "#E0B060", 3, 0.6, 10, 30)
     + static_emus, defs=SUNSET + FIELD + BLUR)
save("emus_field_front", wheat_strokes(1050, H + 60, 700, "#8A5A20", 5, 1.0, 60, 160))

# ---------- gunline (dusk, gun crew left, open field right) ----------
save("gunline_back", f'<rect width="{W}" height="{H}" fill="url(#dk)"/><circle cx="1900" cy="790" r="120" fill="#FFC47A" opacity="0.8"/>'
     + hills(HZ, "#4A2A2A", 5, 50) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fdd)"/>' + wheat_strokes(HZ + 10, 1050, 700, "#B08040", 6, 0.5, 10, 40),
     defs=DUSK + FIELD_D)
save("gunline_front", soldier(250, 1180, 0.95, pose="kneel") + lewis(330, 1180, 1.05) + soldier(120, 1200, 1.0, rifle=False)
     + f'<path d="M0 1180 C 300 1150, 600 1170, 900 1200 L 900 {H} L 0 {H} Z" fill="#1A120E"/>' + wheat_strokes(1200, H + 40, 260, "#3A2A18", 7, 1, 60, 140))
GUN_MUZZLE = (330 + 210 * 1.05, 1180 - 62 * 1.05)

# ---------- gun_crew (daytime, posed with truck) ----------
save("gun_crew_back", f'<rect width="{W}" height="{H}" fill="url(#dy)"/>' + hills(HZ, "#8A7A58", 8, 30) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>'
     + wheat_strokes(HZ + 10, 1000, 600, "#D8B070", 9, 0.6, 10, 30), defs=DAY + FIELD)
save("gun_crew_front", truck(1650, 1150, 1.2, gun=False) + soldier(700, 1180, 1.25) + soldier(950, 1190, 1.25, rifle=False) + soldier(1180, 1180, 1.25, flip=True)
     + lewis(820, 1185, 0.9) + lewis(1060, 1190, 0.9, flip=True) + wheat_strokes(1150, H + 60, 300, "#7A5A30", 10, 1, 50, 120))

# ---------- rain ----------
save("rain_back", f'<rect width="{W}" height="{H}" fill="url(#rn)"/>' + hills(HZ, "#3A3E40", 11, 40) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="#4A4232"/>'
     + "".join(emu(x, HZ + 30, 0.22, "peck") for x in (300, 900, 1600, 2100)) + fog(HZ - 200, HZ + 50, 10, col="#7A8086", op=(0.2, 0.35)),
     defs=grad("rn", [(0, "#3A4048", 1), (1, "#7A8288", 1)]))
save("rain_front", wheat_strokes(1050, H + 60, 600, "#3A3020", 12, 1, 50, 140))

# ---------- dam ----------
save("dam_back", f'<rect width="{W}" height="{H}" fill="url(#ss)"/>' + hills(HZ, "#5A3428", 13, 40)
     + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>'
     + f'<ellipse cx="1200" cy="1000" rx="600" ry="90" fill="#5C4030"/><ellipse cx="1200" cy="1000" rx="540" ry="70" fill="url(#wt)"/>'
     + f'<ellipse cx="1200" cy="985" rx="300" ry="20" fill="#FFD98A" opacity="0.25" filter="url(#b6)"/>',
     defs=SUNSET + FIELD + BLUR + grad("wt", [(0, "#C88A5A", 1), (1, "#5A4A48", 1)]))
save("dam_front", f'<path d="M0 {H} L 0 1050 C 100 980, 250 990, 380 1060 C 420 1100, 460 1200, 480 {H} Z" fill="#1A120E"/>'
     + soldier(240, 1120, 0.85, pose="kneel") + lewis(300, 1110, 0.9) + wheat_strokes(1180, H + 40, 300, "#5A3A18", 14, 1, 50, 120))
DAM_MUZZLE = (300 + 210 * 0.9, 1110 - 62 * 0.9)

# ---------- lookout ----------
save("lookout_back", f'<rect width="{W}" height="{H}" fill="url(#ss)"/><circle cx="1900" cy="600" r="150" fill="#FFD98A" opacity="0.9"/>'
     + f'<path d="M1300 {HZ+40} C 1500 600, 1800 560, 2100 620 C 2250 660, 2350 760, 2400 {HZ} L 2400 {H} L 1300 {H} Z" fill="#3A2218"/>'
     + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>' + f'<path d="M1300 {HZ+1} C 1500 600, 1800 560, 2100 620 C 2250 660, 2350 760, 2400 {HZ} Z" fill="#3A2218"/>'
     + "".join(emu(x, y, s, "peck", flip=f) for x, y, s, f in [(300, 960, 0.5, False), (520, 930, 0.42, True), (760, 980, 0.55, False), (980, 940, 0.45, False), (1150, 1000, 0.6, True), (640, 1060, 0.7, False)])
     + wheat_strokes(HZ + 10, 1100, 700, "#E0B060", 15, 0.6, 10, 40), defs=SUNSET + FIELD)
save("lookout_front", wheat_strokes(1120, H + 60, 400, "#8A5A20", 16, 1, 60, 150))
LOOKOUT_EMU = (1800, 590, 0.75)

# ---------- truck chase (scrolling) ----------
save("truck_back", f'<rect width="{W}" height="{H}" fill="url(#dy)"/>' + hills(760, "#9A8058", 17, 50) + f'<rect y="760" width="{W}" height="{H-760}" fill="#B89058"/>', defs=DAY)
save("truck_ground", "".join(f'<path d="M{x} {y} l 60 0" stroke="#8A6A3A" stroke-width="6" stroke-linecap="round"/>' for x, y in
                             [(random.Random(i).randint(0, W), random.Random(i * 7).randint(800, H)) for i in range(160)])
     + wheat_strokes(820, H, 300, "#9A7A40", 18, 0.8, 10, 50))

# ---------- emu_close (portrait against the sun) ----------
save("emu_close_back", f'<rect width="{W}" height="{H}" fill="url(#ss)"/><circle cx="1350" cy="700" r="430" fill="#FFD27A" opacity="0.95"/>'
     + hills(1020, "#5A3020", 19, 30), defs=SUNSET)
save("emu_close_front", f'<rect y="1000" width="{W}" height="{H-1000}" fill="#2A1810"/>' + wheat_strokes(1000, H + 60, 500, "#4A2E18", 20, 1, 60, 150))
EMU_CLOSE = (1250, 1080, 1.9)

# ---------- fence ----------
save("fence_back", f'<rect width="{W}" height="{H}" fill="url(#dy)"/>' + hills(HZ, "#8A7458", 21, 30) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>'
     + "".join(emu(x, HZ + 40, 0.3, "stand", flip=x > 1200) for x in (400, 700, 1800, 2050))
     + fence(980, -40, W + 100, 160, col="#2A1C12", gap=(1050, 1350), h=150, sw=5), defs=DAY + FIELD)
save("fence_front", wheat_strokes(1080, H + 60, 400, "#8A6A30", 22, 1, 50, 140))

# ---------- trenches (WWI, sepia) ----------
wire = "".join(f'<path d="M{x} 960 l 30 -80 m -30 0 l 30 80" stroke="#2A2420" stroke-width="5"/>' for x in range(80, W, 260))
wire += "".join(f'<path d="M{x} 900 q 65 -40 130 0" stroke="#2A2420" stroke-width="3" fill="none"/>' for x in range(80, W, 130))
save("trenches_back", f'<rect width="{W}" height="{H}" fill="url(#sp)"/><circle cx="600" cy="400" r="120" fill="#E8D8B0" opacity="0.5" filter="url(#b20)"/>'
     + hills(960, "#5A4E40", 23, 30) + wire, defs=grad("sp", [(0, "#8A7A60", 1), (1, "#D8C8A0", 1)]) + BLUR)
save("trenches_front", f'<path d="M0 1050 C 600 1000, 1400 1010, 2400 1040 L 2400 {H} L 0 {H} Z" fill="#2A2420"/>'
     + "".join(soldier(x, 1060 - (x % 3) * 6, 0.85, col="#2A2420", hat="helmet", flip=(i % 2 == 1)) for i, x in enumerate(range(350, 2200, 260))))

# ---------- farm (homestead + windmill tower; fan animated) ----------
save("farm_back", f'<rect width="{W}" height="{H}" fill="url(#dy)"/>' + hills(HZ, "#9A8058", 24, 40) + f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fd)"/>'
     + homestead(900, 900, 0.9) + windmill_tower(1650, 960, 1.0) + fence(960, 1200, 2400, 160, h=70)
     + wheat_strokes(HZ + 10, 1000, 700, "#E0B868", 25, 0.6, 10, 35), defs=DAY + FIELD)
save("farm_front", wheat_strokes(1050, H + 60, 600, "#9A7030", 26, 1, 60, 150))
FAN = (1650, 960 - 430, 1.0)

# ---------- coat (emu + kangaroo on a hill at sunrise) ----------
save("coat_back", f'<rect width="{W}" height="{H}" fill="url(#sr)"/><circle cx="1200" cy="760" r="260" fill="#FFE2A0" opacity="0.95"/>'
     + f'<path d="M0 {H} L 0 980 C 600 820, 1800 820, 2400 980 L 2400 {H} Z" fill="#2A1A14"/>'
     + emu(1000, 900, 1.15, "stand", col="#1A100C") + kangaroo(1420, 900, 1.25, col="#1A100C", flip=True),
     defs=grad("sr", [(0, "#3A4A78", 1), (0.6, "#E08A6A", 1), (1, "#FFD08A", 1)]))
save("coat_front", '')

# ---------- title (uses emus_field) / newspapers ----------
newspaper("paper_a", "OCTOBER 1932", "MACHINE GUNS", "FOR EMUS?", "Wheatbelt farmers appeal", "to the Minister of Defence", seed=21)
newspaper("paper_b", "NOVEMBER 1932", "EMUS WIN", "ROUND ONE", "Troops withdrawn from the", "wheatbelt after poor results", seed=22)
newspaper("paper_c", "1934", "EMU", "BOUNTIES", "More than 57,000 claimed", "in six months", seed=23)
newspaper("report", "DECEMBER 1932", "MEREDITH'S", "REPORT", "986 birds claimed with", "9,860 rounds of ammunition", seed=24)

# ---------- map (schematic) ----------
grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#8A7350" stroke-width="2" opacity="0.25"/>' for x in range(0, W + 1, 150))
grid += "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#8A7350" stroke-width="2" opacity="0.25"/>' for y in range(0, H + 1, 150))
save("map_back", f'<rect width="{W}" height="{H}" fill="#E6D6B2"/>{grid}'
     f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="#5A4630" stroke-width="6"/>'
     f'<path d="M0 0 L 420 0 C 460 300, 400 600, 520 900 C 560 1050, 520 1200, 560 {H} L 0 {H} Z" fill="#B8CCD0" opacity="0.7"/>'
     f'<ellipse cx="1180" cy="700" rx="520" ry="330" fill="#D8A850" opacity="0.35"/>'
     f'<text x="1180" y="1080" font-family="Playfair Display SC" font-weight="900" font-size="46" fill="#7A5A30" text-anchor="middle">THE WHEATBELT</text>'
     f'<text x="230" y="700" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="50" fill="#4A6670" text-anchor="middle">Indian Ocean</text>'
     f'<text x="{W-90}" y="{H-80}" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="34" fill="#5A4630" text-anchor="end">Western Australia, 1932 · simplified, not to scale</text>'
     f'<g transform="translate(2180 200)"><circle r="80" fill="none" stroke="#5A4630" stroke-width="4"/><path d="M0 -95 L 18 0 L 0 95 L -18 0 Z" fill="#5A4630"/><text y="-110" font-family="Playfair Display SC" font-weight="900" font-size="40" fill="#5A4630" text-anchor="middle">N</text></g>')
print("ep2 scenes done")
