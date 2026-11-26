import sys, shutil
sys.argv = ["x"]
src = open("ep4/scenes.py").read().split("# ---------- sprites")[0]
exec(src)
W2, H2 = 1280, 720
body = (f'<rect width="{W2}" height="{H2}" fill="url(#sk)"/><rect y="400" width="{W2}" height="320" fill="url(#se)"/>'
        + f'<g transform="rotate(-8 330 520)">{ironclad(330, 520, 0.85, "victoria")}</g>'
        + f'<g transform="translate(880 0) scale(-0.6 1) translate(-880 0)">{ironclad(880, 560, 0.85, "camperdown")}</g>'
        + '<path d="M560 520 C 580 430, 600 380, 620 300 C 635 380, 650 360, 665 290 C 680 390, 700 420, 730 520 Z" fill="#F0F4F6" opacity="0.9"/>'
        + f'<rect y="560" width="{W2}" height="160" fill="#1E5A80" opacity="0.92"/>'
        + f'<text x="1240" y="140" font-family="Anton" font-size="104" fill="{CREAM}" text-anchor="end" stroke="#0A0E12" stroke-width="10" paint-order="stroke">RAMMED BY</text>'
        + f'<text x="1240" y="255" font-family="Anton" font-size="104" fill="#FFC94A" text-anchor="end" stroke="#0A0E12" stroke-width="10" paint-order="stroke">ITS OWN FLEET</text>'
        + f'<rect x="1060" y="600" width="180" height="66" rx="12" fill="{RED}"/><text x="1150" y="648" font-family="Anton" font-size="46" fill="{CREAM}" text-anchor="middle">1893</text>')
SKY2 = grad("sk", [(0, "#4F8CC0", 1), (1, "#E8EEF0", 1)]); SEA2 = grad("se", [(0, "#3A7AA0", 1), (1, "#0E2E44", 1)])
save("thumb", body, w=W2, h=H2, defs=SKY2 + SEA2)
shutil.copy("ep4/layers/thumb.png", "out/Thumbnail_HMSVictoria.png")
