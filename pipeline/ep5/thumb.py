import sys, shutil
sys.path.insert(0, "ep5")
sys.argv = ["x"]
exec(open("ep5/scenes.py").read().split("# ---------- sprites")[0])
W2, H2 = 1280, 720
body = (f'<rect width="{W2}" height="{H2}" fill="url(#neb)"/>{starfield(200, 3)}{mars(330, 470, 330)}'
        + orbiter(760, 560, 0.8).replace('<g transform', '<g opacity="1" transform')
        + f'<text x="1240" y="150" font-family="Anton" font-size="112" fill="{CREAM}" text-anchor="end" stroke="#05060C" stroke-width="10" paint-order="stroke">LOST TO A</text>'
        + f'<text x="1240" y="275" font-family="Anton" font-size="112" fill="#FFC94A" text-anchor="end" stroke="#05060C" stroke-width="10" paint-order="stroke">UNITS ERROR</text>'
        + f'<rect x="980" y="320" width="260" height="66" rx="12" fill="{RED}"/><text x="1110" y="368" font-family="Anton" font-size="44" fill="{CREAM}" text-anchor="middle">LB vs N · 1999</text>')
save("thumb", body, w=W2, h=H2, defs=SPACE + MARS)
shutil.copy("ep5/layers/thumb.png", "out/Thumbnail_MarsClimateOrbiter.png")
