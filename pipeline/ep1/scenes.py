import sys, random
sys.path.insert(0, "long")
from art import *

# ---------- shared sprites ----------
save("beam", grad("bm", [(0, "#FFF6DA", 0.85), (0.6, "#FFF6DA", 0.25), (1, "#FFF6DA", 0)], vertical=False)
     and '<polygon points="0,200 1900,0 1900,400" fill="url(#bm)" filter="url(#b6)"/>', w=1900, h=400,
     defs=grad("bm", [(0, "#FFF6DA", 0.85), (0.6, "#FFF6DA", 0.25), (1, "#FFF6DA", 0)], vertical=False))
save("flash", '<circle cx="150" cy="150" r="150" fill="url(#fl)"/>', w=300, h=300,
     defs='<radialGradient id="fl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.3" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="#D9482B" stop-opacity="0"/></radialGradient>')
save("splash", '<path d="M40 300 C 60 200, 80 120, 100 20 C 115 100, 125 60, 140 10 C 150 110, 170 150, 200 70 C 205 170, 230 220, 260 300 Z" fill="#E8EEF3" opacity="0.85"/><ellipse cx="150" cy="300" rx="140" ry="22" fill="#E8EEF3" opacity="0.6"/>', w=300, h=330)
save("crane", trawler(380, 430, 1.55), w=760, h=560)
save("stamp", f'<g transform="rotate(-12 330 130)"><rect x="20" y="20" width="620" height="220" rx="18" fill="none" stroke="{RED}" stroke-width="14"/>'
     f'<text x="330" y="150" font-family="Anton" font-size="120" fill="{RED}" text-anchor="middle">£66,000</text>'
     f'<text x="330" y="215" font-family="Montserrat" font-weight="800" font-size="42" fill="{RED}" text-anchor="middle" letter-spacing="8">COMPENSATION</text></g>', w=680, h=330)
save("desk", '<rect width="2400" height="1350" fill="url(#dk)"/>', defs='<radialGradient id="dk" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3B2A1C"/><stop offset="1" stop-color="#120C08"/></radialGradient>')
# telegram slips for the "rumours" scene
TEL = ["JAPANESE OFFICERS WITH TORPEDOES SEEN IN BALTIC", "BRITAIN BUILT TORPEDO BOATS FOR JAPAN", "MINES REPORTED IN THE STRAITS",
       "SUBMARINES SUSPECTED", "BALLOONS SIGHTED. FOUR ENEMY CRUISERS", "TORPEDO BOATS LEAVING NORWAY"]
for i, t in enumerate(TEL):
    words, lines, cur = t.split(), [], ""
    for w in words:
        if len(cur + " " + w) > 22: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    lines.append(cur)
    txt = "".join(f'<text x="40" y="{200 + j*58}" font-family="DejaVu Sans Mono" font-weight="bold" font-size="40" fill="#1B1712">{l}</text>' for j, l in enumerate(lines))
    save(f"tel{i}", f'<rect x="10" y="10" width="760" height="{260 + len(lines)*58}" fill="#E9DFC6" stroke="#3A3226" stroke-width="3"/>'
         f'<text x="40" y="80" font-family="Playfair Display SC" font-weight="900" font-size="44" fill="#1B1712">TELEGRAM</text>'
         f'<line x1="40" y1="110" x2="740" y2="110" stroke="#1B1712" stroke-width="3"/><text x="40" y="150" font-family="DejaVu Sans Mono" font-size="28" fill="#5A4E3C">URGENT  ·  1904</text>{txt}',
         w=780, h=280 + len(lines) * 58)

# ---------- night_fleet ----------
HZ = 900
save("night_fleet_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{stars(260, HZ-120)}'
     f'<circle cx="1800" cy="300" r="240" fill="url(#moon)"/><circle cx="1800" cy="300" r="70" fill="{CREAM}"/>'
     f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 16, H, "#7F95AA", 0.2) +
     f'<path d="M1760 {HZ} L 1840 {HZ} L 1960 {H} L 1640 {H} Z" fill="{CREAM}" opacity="0.18" filter="url(#b20)"/>',
     defs=grad("se", [(0, "#1A2B3D", 1), (1, "#05090F", 1)]) + grad("sk", [(0, "#060C14", 1), (0.6, "#14253A", 1), (1, "#2C4258", 1)]) +
     f'<radialGradient id="moon"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.45"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></radialGradient>')
save("night_fleet_front", "".join(battleship(x, HZ + 6, s) for x, s in [(1900, 1.15), (1250, 0.85), (760, 0.62), (390, 0.46), (120, 0.36)])
     + fog(HZ - 200, HZ + 60, 14))

# ---------- attack / crane / aurora (searchlight night) ----------
HZ2 = 760
save("attack_back", f'<rect width="{W}" height="{H}" fill="url(#s2)"/>{stars(110, HZ2-200, (0.1, 0.4), 4)}'
     + "".join(battleship(x, HZ2 + 4, s, col="#03070C", smoke="#22303E") for x, s in [(150, 0.55), (520, 0.42), (820, 0.33), (1050, 0.26)])
     + f'<rect y="{HZ2}" width="{W}" height="{H-HZ2}" fill="url(#se2)"/>' + waves(HZ2 + 16, H, "#6F879E", 0.2),
     defs=grad("s2", [(0, "#05090E", 1), (1, "#1B2B3C", 1)]) + grad("se2", [(0, "#17283A", 1), (1, "#04080D", 1)]))
save("attack_front", trawler(1500, HZ2 + 150, 0.8) + trawler(2050, HZ2 + 110, 0.6, flip=True) + trawler(1150, HZ2 + 90, 0.5)
     + trawler(2250, HZ2 + 260, 0.7) + f'<rect y="1180" width="{W}" height="{H-1180}" fill="url(#fw)"/>' + waves(1200, H, "#8AA2B8", 0.22, 50),
     defs=grad("fw", [(0, "#0B1520", 0), (0.3, "#0B1520", 1), (1, "#03060A", 1)]))
save("aurora_back", f'<rect width="{W}" height="{H}" fill="url(#s2)"/>{stars(110, HZ2-200, (0.1, 0.4), 5)}'
     + f'<rect y="{HZ2}" width="{W}" height="{H-HZ2}" fill="url(#se2)"/>' + waves(HZ2 + 16, H, "#6F879E", 0.2)
     + "".join(battleship(x, HZ2 + 4, s, col="#03070C", smoke="#22303E", flip=True) for x, s in [(2150, 0.5), (1850, 0.38)]),
     defs=grad("s2", [(0, "#05090E", 1), (1, "#1B2B3C", 1)]) + grad("se2", [(0, "#17283A", 1), (1, "#04080D", 1)]))
save("aurora_front", cruiser3(900, HZ2 + 220, 1.25) + cruiser3(380, HZ2 + 80, 0.6) + fog(HZ2 - 100, HZ2 + 200, 8, seed=9))

# ---------- port_arthur (night harbour) ----------
HZ3 = 820
hills = f'<path d="M0 {HZ3} L 0 600 C 300 520, 500 640, 800 560 C 1100 480, 1300 620, 1600 540 C 1900 460, 2150 600, 2400 520 L 2400 {HZ3} Z" fill="#0A1018"/>'
save("port_arthur_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{stars(200, 500, seed=7)}{hills}'
     + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFD98A" opacity="0.7"/>' for x, y in [(300, 700), (340, 712), (900, 690), (960, 700), (1500, 700), (1560, 690), (2000, 680)]),
     defs=grad("sk", [(0, "#050A12", 1), (1, "#1C2C40", 1)]))
save("port_arthur_front", "".join(battleship(x, HZ3 + 40, s, smoke=None, windows=True) for x, s in [(500, 0.8), (1200, 0.95), (1950, 0.75)])
     + f'<rect y="{HZ3+38}" width="{W}" height="{H-HZ3}" fill="url(#se)"/>' + waves(HZ3 + 50, H, "#7F95AA", 0.18)
     + "".join(f'<rect x="{x}" y="{HZ3+40}" width="70" height="{H}" fill="#FFD98A" opacity="0.06" filter="url(#b20)"/>' for x in (480, 1180, 1930)),
     defs=grad("se", [(0, "#16263A", 1), (1, "#04080D", 1)]))

# ---------- fleet_day / britain / battle (daylight grey) ----------
HZ4 = 820
day_defs = grad("dsk", [(0, "#6C7A86", 1), (1, "#AEB8BE", 1)]) + grad("dse", [(0, "#4D5D69", 1), (1, "#1E2A33", 1)])
clouds = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#C9D0D4" opacity="0.35" filter="url(#b40)"/>'
                 for x, y, rx, ry in [(300, 200, 420, 80), (1100, 330, 500, 90), (1900, 180, 450, 70), (1500, 520, 600, 60)])
save("fleet_day_back", f'<rect width="{W}" height="{H}" fill="url(#dsk)"/>{clouds}<rect y="{HZ4}" width="{W}" height="{H-HZ4}" fill="url(#dse)"/>'
     + waves(HZ4 + 14, H, "#D7DEE2", 0.18), defs=day_defs)
save("fleet_day_front", "".join(battleship(x, HZ4 + 8 + i * 4, s, col="#1A232C", lights=False, smoke="#2F3A44") for i, (x, s) in
                                enumerate([(2050, 1.2), (1450, 0.95), (980, 0.75), (620, 0.6), (330, 0.48), (90, 0.4)])))
save("britain_front", "".join(battleship(x, HZ4 + 8, s, col="#202A33", lights=False, smoke="#38434D", flip=True) for x, s in
                              [(350, 1.15), (950, 0.95), (1450, 0.8), (1850, 0.66), (2180, 0.55)]))
save("battle_back", f'<rect width="{W}" height="{H}" fill="url(#dsk)"/>{clouds}{fog(300, 800, 12, col="#4A4F52", op=(0.25, 0.45))}'
     f'<rect y="{HZ4}" width="{W}" height="{H-HZ4}" fill="url(#dse)"/>' + waves(HZ4 + 14, H, "#D7DEE2", 0.15)
     + "".join(battleship(x, HZ4 + 2, s, col="#2A2F33", lights=False, smoke="#3D4246", flip=True) for x, s in [(1700, 0.45), (1950, 0.4), (2200, 0.35)]),
     defs=grad("dsk", [(0, "#4F575E", 1), (1, "#8E8A80", 1)]) + grad("dse", [(0, "#3D4A54", 1), (1, "#161E25", 1)]))
save("battle_front", "".join(battleship(x, HZ4 + 30 + i * 10, s, col="#151B21", lights=False, smoke="#262C31") for i, (x, s) in
                             enumerate([(1100, 1.05), (520, 0.8), (150, 0.6)])))

# ---------- kamchatka ----------
save("kamchatka_back", f'<rect width="{W}" height="{H}" fill="url(#sk)"/>{stars(160, 600, (0.1, 0.5), 8)}'
     f'<rect y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#se)"/>' + waves(HZ + 16, H, "#6F879E", 0.2)
     + schooner(500, HZ + 10, 0.55) + merchant(900, HZ + 6, 0.35, flip=True) + trawler(260, HZ + 4, 0.35),
     defs=grad("sk", [(0, "#060B12", 1), (1, "#213347", 1)]) + grad("se", [(0, "#16263A", 1), (1, "#04080D", 1)]))
save("kamchatka_front", merchant(1750, HZ + 120, 1.25) + fog(HZ - 120, HZ + 100, 10, seed=12))

# ---------- hull (dawn harbour) ----------
dock = (f'<path d="M0 760 L 0 520 L 180 520 L 180 470 L 380 470 L 380 560 L 560 560 L 560 430 L 600 430 L 600 300 L 640 300 L 640 430 L 800 430 L 800 600 L 1000 600 L 1000 500 L 1200 500 L 1200 760 Z" fill="#1A1216"/>'
        f'<path d="M1500 760 L 1500 560 L 1700 560 L 1700 480 L 1900 480 L 1900 590 L 2100 590 L 2100 520 L 2400 520 L 2400 760 Z" fill="#1A1216"/>'
        f'<path d="M1320 760 L 1320 380 L 1340 380 L 1340 760 Z M1330 390 L 1480 470" stroke="#1A1216" stroke-width="14" fill="#1A1216"/>')
save("hull_back", f'<rect width="{W}" height="{H}" fill="url(#dawn)"/><circle cx="1250" cy="760" r="160" fill="#FFD7A0" opacity="0.8" filter="url(#b20)"/>{dock}'
     f'<rect y="760" width="{W}" height="{H-760}" fill="url(#dsea)"/>' + waves(776, H, "#FFC7A0", 0.15),
     defs=grad("dawn", [(0, "#2A2440", 1), (0.6, "#B4606A", 1), (1, "#F2A47A", 1)]) + grad("dsea", [(0, "#5A3A4A", 1), (1, "#120C12", 1)]))
save("hull_front", trawler(900, 1000, 1.0, col="#140E12", lights=False) + trawler(1650, 900, 0.7, col="#140E12", lights=False, flip=True)
     + trawler(380, 880, 0.55, col="#140E12", lights=False))

# ---------- vigo (sunny Spanish bay) ----------
save("vigo_back", f'<rect width="{W}" height="{H}" fill="url(#vsk)"/>'
     f'<path d="M0 760 C 300 520, 600 560, 900 600 C 1200 640, 1500 480, 1900 540 C 2100 570, 2300 520, 2400 560 L 2400 760 Z" fill="#7C8A5A"/>'
     f'<path d="M0 760 C 400 660, 800 700, 1200 690 C 1600 680, 2000 640, 2400 690 L 2400 760 Z" fill="#5E6E44"/>'
     + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#EFE6D2"/><rect x="{x}" y="{y-12}" width="{w}" height="14" fill="#B5583A"/>'
               for x, y, w, h in [(300, 690, 60, 40), (380, 700, 50, 34), (460, 685, 70, 45), (560, 700, 40, 30), (640, 692, 66, 38)])
     + f'<rect y="760" width="{W}" height="{H-760}" fill="url(#vse)"/>' + waves(776, H, "#E6F1F5", 0.2),
     defs=grad("vsk", [(0, "#4F8FC0", 1), (1, "#CFE3EE", 1)]) + grad("vse", [(0, "#3C7FA0", 1), (1, "#163A4E", 1)]))
save("vigo_front", "".join(battleship(x, 800 + i * 20, s, col="#1C2530", lights=False, smoke=None) for i, (x, s) in enumerate([(1500, 0.6), (1950, 0.75), (1050, 0.5)])))

# ---------- madagascar (tropical sunset) ----------
save("madagascar_back", f'<rect width="{W}" height="{H}" fill="url(#msk)"/><circle cx="1600" cy="720" r="180" fill="#FFD27A" opacity="0.9"/>'
     f'<path d="M0 780 C 300 700, 500 720, 700 760 L 700 780 Z" fill="#2A1410"/>'
     f'<rect y="780" width="{W}" height="{H-780}" fill="url(#mse)"/><path d="M1540 780 L 1660 780 L 1760 {H} L 1440 {H} Z" fill="#FFD27A" opacity="0.25" filter="url(#b20)"/>'
     + waves(796, H, "#FFB070", 0.15) + "".join(battleship(x, 790, s, col="#2A1410", lights=False, smoke=None) for x, s in [(1000, 0.55), (1400, 0.42), (1900, 0.5), (2250, 0.36)]),
     defs=grad("msk", [(0, "#3A1E3A", 1), (0.6, "#D0603A", 1), (1, "#F6B060", 1)]) + grad("mse", [(0, "#8A4030", 1), (1, "#1A0C0A", 1)]))
save("madagascar_front", palm(200, 1350, 1.7) + palm(420, 1350, 1.3) + palm(2250, 1350, 1.5)
     + f'<path d="M0 1350 L 0 1150 C 300 1120, 600 1200, 800 1350 Z" fill="#120A08"/><path d="M2400 1350 L 2400 1180 C 2200 1160, 2050 1250, 1950 1350 Z" fill="#120A08"/>')

# ---------- tsushima ----------
HZ5 = 860
r = random.Random(5)
smk = "".join(f'<ellipse cx="{x}" cy="{HZ5-250-r.randint(0,450)}" rx="{r.randint(150,320)}" ry="{r.randint(80,160)}" fill="#1A1110" opacity="{r.uniform(0.35,0.6):.2f}" filter="url(#b40)"/>' for x in range(-50, W + 100, 140))
save("tsushima_back", f'<rect width="{W}" height="{H}" fill="url(#t)"/>{smk}<rect y="{HZ5}" width="{W}" height="{H-HZ5}" fill="url(#ts)"/>' + waves(HZ5 + 16, H, "#E0602F", 0.16),
     defs=grad("t", [(0, "#1A0B0A", 1), (0.6, "#7A2216", 1), (1, "#E0602F", 1)]) + grad("ts", [(0, "#3A1610", 1), (1, "#070303", 1)]))
fire = '<radialGradient id="fi"><stop offset="0" stop-color="#FFD27A"/><stop offset="0.4" stop-color="#FF7A2E" stop-opacity="0.8"/><stop offset="1" stop-color="#FF7A2E" stop-opacity="0"/></radialGradient>'
save("tsushima_front", "".join(f'<g transform="rotate({rot} {x} {HZ5})"><circle cx="{x-20}" cy="{HZ5-120*s}" r="{170*s}" fill="url(#fi)"/>{battleship(x, HZ5 + 60*s, s, col="#0C0605", lights=False, smoke="#120B0A")}</g>'
                               for x, s, rot in [(1700, 1.0, 14), (900, 0.7, -18), (350, 0.45, 8), (2200, 0.5, -6)]), defs=fire)

# ---------- aurora epilogue (dusk river city) ----------
city = ""
for x in range(0, W, 120):
    h = random.Random(x).randint(80, 200)
    city += f'<rect x="{x}" y="{760-h}" width="110" height="{h}" fill="#1C1A2C"/>'
city += ('<rect x="560" y="420" width="16" height="340" fill="#1C1A2C"/><path d="M568 300 L 560 420 L 576 420 Z" fill="#C9A04A"/>'
         '<ellipse cx="1500" cy="560" rx="120" ry="110" fill="#1C1A2C"/><rect x="1380" y="560" width="240" height="200" fill="#1C1A2C"/><rect x="1494" y="420" width="12" height="40" fill="#C9A04A"/>')
save("aurora_epi_back", f'<rect width="{W}" height="{H}" fill="url(#ep)"/>{city}<rect y="760" width="{W}" height="{H-760}" fill="url(#er)"/>' + waves(776, H, "#C9B0E0", 0.12),
     defs=grad("ep", [(0, "#1A1838", 1), (0.7, "#7A5A8A", 1), (1, "#E0A890", 1)]) + grad("er", [(0, "#3A3050", 1), (1, "#0C0A14", 1)]))
save("aurora_epi_front", cruiser3(1200, 960, 1.6, col="#0E0C18", windows=True))

# ---------- memorial (Hull, sunset) ----------
statue = ('<g transform="translate(1200 1350)"><rect x="-170" y="-430" width="340" height="430" fill="#141018"/><rect x="-200" y="-470" width="400" height="50" fill="#141018"/>'
          '<rect x="-210" y="-30" width="420" height="40" fill="#141018"/>'
          '<path d="M-60 -470 L -70 -760 L -40 -900 L 40 -900 L 70 -760 L 60 -470 Z" fill="#141018"/>'
          '<circle cx="0" cy="-950" r="55" fill="#141018"/><path d="M-80 -965 L 80 -965 L 60 -1010 L -60 -1010 Z" fill="#141018"/>'
          '<path d="M40 -880 L 120 -760 L 100 -740 L 30 -820 Z" fill="#141018"/>'
          '<text x="0" y="-240" font-family="Playfair Display SC" font-weight="900" font-size="44" fill="#8F7A55" text-anchor="middle">IN MEMORY</text>'
          '<text x="0" y="-180" font-family="Playfair Display SC" font-weight="900" font-size="40" fill="#8F7A55" text-anchor="middle">OCT 1904</text></g>')
save("memorial_back", f'<rect width="{W}" height="{H}" fill="url(#mm)"/><circle cx="1650" cy="900" r="200" fill="#FFCF8A" opacity="0.8" filter="url(#b20)"/>'
     f'<path d="M0 1100 L 0 960 L 300 960 L 300 900 L 520 900 L 520 1000 L 800 1000 L 800 940 L 1000 940 L 1000 1100 Z M1500 1100 L 1500 980 L 1800 980 L 1800 920 L 2100 920 L 2100 1000 L 2400 1000 L 2400 1100 Z" fill="#2A1E28"/>'
     f'<rect y="1100" width="{W}" height="250" fill="#1A1218"/>', defs=grad("mm", [(0, "#3A2A48", 1), (0.7, "#C07060", 1), (1, "#F0B080", 1)]))
save("memorial_front", statue)

# ---------- newspapers ----------
newspaper("paper1", "MONDAY, OCTOBER 24, 1904", "THE RUSSIAN", "OUTRAGE", "Baltic Fleet fires on Hull trawlers", "on the Dogger Bank")
newspaper("paper2", "FEBRUARY 1905", "INQUIRY", "IN PARIS", "International commission reports", "on the North Sea incident", seed=12)
newspaper("treaty", "SEPTEMBER 1905", "PEACE", "SIGNED", "Russia and Japan sign treaty", "at Portsmouth", seed=13)
newspaper("court", "1906", "ADMIRALS", "ON TRIAL", "Tsushima commanders face", "courts martial", seed=14)

# ---------- map (schematic, not to scale) ----------
r = random.Random(2)
grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#8A7350" stroke-width="2" opacity="0.25"/>' for x in range(0, W + 1, 150))
grid += "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#8A7350" stroke-width="2" opacity="0.25"/>' for y in range(0, H + 1, 150))
save("map_back", f'<rect width="{W}" height="{H}" fill="#E6D6B2"/>{grid}'
     f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="#5A4630" stroke-width="6"/>'
     f'<rect x="46" y="46" width="{W-92}" height="{H-92}" fill="none" stroke="#5A4630" stroke-width="2"/>'
     f'<text x="{W-90}" y="{H-80}" font-family="Playfair Display" font-style="italic" font-weight="600" font-size="34" fill="#5A4630" text-anchor="end">The voyage of the Second Pacific Squadron, 1904–05 · route simplified, not to scale</text>'
     f'<g transform="translate(2180 200)"><circle r="80" fill="none" stroke="#5A4630" stroke-width="4"/><path d="M0 -95 L 18 0 L 0 95 L -18 0 Z" fill="#5A4630"/><text y="-110" font-family="Playfair Display SC" font-weight="900" font-size="40" fill="#5A4630" text-anchor="middle">N</text></g>')
print("scenes done")
