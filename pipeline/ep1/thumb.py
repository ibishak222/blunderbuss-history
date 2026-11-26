import sys
sys.path.insert(0, "long")
from art import *
W2, H2 = 1280, 720
body = (f'<rect width="{W2}" height="{H2}" fill="url(#s)"/>'
        f'<polygon points="1180,420 60,250 60,620" fill="url(#bm)"/>'
        f'<rect y="470" width="{W2}" height="250" fill="url(#se)"/>'
        + battleship(1080, 478, 0.75, col="#04070C", smoke="#1E2A36", flip=True)
        + '<circle cx="880" cy="420" r="70" fill="url(#fl)"/>'
        + trawler(300, 560, 1.05, col="#1E2A36")
        + '<path d="M150 360 C 170 280, 190 230, 210 160 C 225 240, 240 210, 255 150 C 265 250, 290 280, 320 360 Z" fill="#E8EEF3" opacity="0.8" transform="translate(470 170) scale(0.6)"/>'
        f'<text x="1240" y="150" font-family="Anton" font-size="128" fill="{CREAM}" text-anchor="end" stroke="#05080C" stroke-width="10" paint-order="stroke">THEY SHOT</text>'
        f'<text x="1240" y="280" font-family="Anton" font-size="128" fill="#FFC94A" text-anchor="end" stroke="#05080C" stroke-width="10" paint-order="stroke">FISHERMEN?!</text>'
        f'<rect x="1040" y="610" width="200" height="70" rx="12" fill="{RED}"/><text x="1140" y="660" font-family="Anton" font-size="48" fill="{CREAM}" text-anchor="middle">1904</text>')
defs = (grad("s", [(0, "#05090E", 1), (1, "#22364C", 1)]) + grad("se", [(0, "#17283A", 1), (1, "#03060A", 1)])
        + grad("bm", [(0, "#FFF6DA", 0), (1, "#FFF6DA", 0.75)], vertical=False)
        + '<radialGradient id="fl"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.35" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="#D9482B" stop-opacity="0"/></radialGradient>')
save("thumb", body, w=W2, h=H2, defs=defs)
import shutil; shutil.copy("long/layers/thumb.png", "out/Thumbnail_DoggerBank.png")
