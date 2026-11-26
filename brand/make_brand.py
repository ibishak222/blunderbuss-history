import subprocess, random
GUN = open("brand/blunderbuss.svgfrag").read()
NAVY, CREAM, RED, BRASS, INK2 = "#14202E", "#F1E4C8", "#D9482B", "#C9A04A", "#1E2F42"

def puff(cx, cy, r, fill=CREAM, stroke=NAVY, sw=10, seed=3):
    random.seed(seed)
    blobs = [(0, 0, 1.0), (-0.75, 0.25, 0.7), (0.78, 0.18, 0.72), (-0.35, -0.6, 0.66),
             (0.42, -0.62, 0.68), (0.05, 0.55, 0.62), (-0.95, -0.25, 0.5), (1.0, -0.3, 0.5)]
    outline = "".join(f'<circle cx="{cx+dx*r:.0f}" cy="{cy+dy*r:.0f}" r="{s*r*0.62+sw:.0f}" fill="{stroke}"/>' for dx, dy, s in blobs)
    inner = "".join(f'<circle cx="{cx+dx*r:.0f}" cy="{cy+dy*r:.0f}" r="{s*r*0.62:.0f}" fill="{fill}"/>' for dx, dy, s in blobs)
    return outline + inner

def spark(cx, cy, r, color=RED):
    pts = []
    import math
    for i in range(16):
        a = math.pi * 2 * i / 16
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx+rr*math.cos(a):.0f},{cy+rr*math.sin(a):.0f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="{NAVY}" stroke-width="10" stroke-linejoin="round"/>'

def icon(x, y, scale, rot=-20, puff_on=True):
    # gun + muzzle spark + puff, local coords
    p = ""
    if puff_on:
        p += spark(585, 105, 70)
        p += puff(690, 70, 95)
        p += f'<text x="690" y="96" font-family="Anton" font-size="78" fill="{RED}" text-anchor="middle" transform="rotate(20 690 70)">OOPS</text>'
    return f'<g transform="translate({x} {y}) scale({scale}) rotate({rot} 300 120)"><g transform="translate(60 -55) scale(0.82 1.45)">{GUN}</g><g transform="translate(-40 0)">{p}</g></g>'

# ---------- LOGO 1000x1000 ----------
logo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
<defs><radialGradient id="bg" cx="50%" cy="42%" r="60%"><stop offset="0" stop-color="#22374E"/><stop offset="1" stop-color="{NAVY}"/></radialGradient></defs>
<rect width="1000" height="1000" fill="{NAVY}"/>
<circle cx="500" cy="500" r="500" fill="url(#bg)"/>
<circle cx="500" cy="500" r="455" fill="none" stroke="{BRASS}" stroke-width="14"/>
<circle cx="500" cy="500" r="430" fill="none" stroke="{BRASS}" stroke-width="4" opacity="0.6"/>
{icon(150, 250, 0.95, rot=-16)}
<text x="500" y="730" font-family="Playfair Display SC" font-weight="900" font-size="86" fill="{CREAM}" text-anchor="middle" letter-spacing="3">BLUNDERBUSS</text>
<text x="500" y="800" font-family="Montserrat" font-weight="700" font-size="40" fill="{BRASS}" text-anchor="middle" letter-spacing="14">HISTORY</text>
</svg>'''
open("brand/logo.svg", "w").write(logo)

# icon-only version for tiny sizes (profile pic is shown ~98px)
logo_min = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
<defs><radialGradient id="bg" cx="50%" cy="42%" r="60%"><stop offset="0" stop-color="#22374E"/><stop offset="1" stop-color="{NAVY}"/></radialGradient></defs>
<rect width="1000" height="1000" fill="url(#bg)"/>
<circle cx="500" cy="500" r="455" fill="none" stroke="{BRASS}" stroke-width="16"/>
{icon(25, 385, 1.18, rot=-16)}
</svg>'''
open("brand/logo_icon.svg", "w").write(logo_min)

# ---------- BANNER 2560x1440 (safe area 1546x423 centred) ----------
random.seed(7)
stars = "".join(f'<circle cx="{random.randint(0,2560)}" cy="{random.randint(0,900)}" r="{random.choice([1.5,2,2.5,3])}" fill="{CREAM}" opacity="{random.uniform(0.15,0.5):.2f}"/>' for _ in range(160))
# map-ish grid lines
grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="1440" stroke="{BRASS}" stroke-width="2" opacity="0.07"/>' for x in range(0, 2561, 160))
grid += "".join(f'<line x1="0" y1="{y}" x2="2560" y2="{y}" stroke="{BRASS}" stroke-width="2" opacity="0.07"/>' for y in range(0, 1441, 160))
def ship(x, y, s, op):
    return (f'<g transform="translate({x} {y}) scale({s})" opacity="{op}" fill="#0B141E">'
            '<path d="M0 60 L 40 90 L 520 90 L 560 60 Z"/><rect x="120" y="20" width="230" height="42"/>'
            '<rect x="170" y="-40" width="34" height="62"/><rect x="240" y="-30" width="34" height="52"/>'
            '<rect x="70" y="40" width="70" height="12"/><rect x="360" y="34" width="110" height="10"/>'
            '<rect x="300" y="-90" width="8" height="110"/><rect x="100" y="-70" width="8" height="90"/></g>')
waves = "".join(f'<path d="M{x} {1180+ (i%3)*30} q 40 -22 80 0 t 80 0" fill="none" stroke="{CREAM}" stroke-width="4" opacity="0.10"/>'
                for i, x in enumerate(range(-40, 2600, 170)))
banner = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E1823"/><stop offset="0.62" stop-color="{INK2}"/><stop offset="1" stop-color="#0B141E"/></linearGradient>
 <radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{RED}" stop-opacity="0.35"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
 <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.28"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></linearGradient>
</defs>
<rect width="2560" height="1440" fill="url(#sky)"/>
{grid}{stars}
<polygon points="2260,900 1500,620 1500,760" fill="url(#beam)"/>
<polygon points="300,920 1060,640 1060,780" fill="url(#beam)" transform="scale(-1 1) translate(-2560 0) scale(-1 1) translate(-2560 0)"/>
{ship(1950, 860, 0.9, 0.95)}{ship(120, 880, 0.8, 0.9)}
<rect x="0" y="960" width="2560" height="480" fill="#0B141E" opacity="0.9"/>
{waves}
<ellipse cx="1280" cy="720" rx="900" ry="300" fill="url(#glow)"/>
<!-- safe area content -->
{icon(455, 625, 0.56, rot=-14)}
<text x="1440" y="745" font-family="Playfair Display SC" font-weight="900" font-size="150" fill="{CREAM}" text-anchor="middle" letter-spacing="6">BLUNDERBUSS</text>
<text x="1440" y="812" font-family="Montserrat" font-weight="600" font-size="44" fill="{BRASS}" text-anchor="middle" letter-spacing="3">The full stories of history's biggest blunders</text>
<rect x="1170" y="845" width="540" height="64" rx="32" fill="{RED}"/>
<text x="1440" y="889" font-family="Montserrat" font-weight="800" font-size="30" fill="{CREAM}" text-anchor="middle" letter-spacing="3">NEW EPISODES WEEKLY</text>
</svg>'''
open("brand/banner.svg", "w").write(banner)

for name, w in [("logo", 1000), ("logo_icon", 1000), ("banner", 2560)]:
    subprocess.run(["rsvg-convert", "-w", str(w), f"brand/{name}.svg", "-o", f"brand/{name}.png"], check=True)
print("ok")
