import sys, shutil
sys.path.insert(0, "ep3")
from art3 import *
W2, H2 = 1280, 720
body = (f'<rect width="{W2}" height="{H2}" fill="url(#s)"/>' + skyline(470, "#3A3E4A", 3).replace('width="', 'width="')
        + f'<rect y="470" width="{W2}" height="250" fill="#24384A"/>'
        + f'<g transform="rotate(-28 380 560)">{galleon(380, 560, 0.62)}</g>'
        + f'<rect y="560" width="{W2}" height="160" fill="#1E3040" opacity="0.92"/>' + "".join(f'<path d="M{x} 600 q 30 -12 60 0" stroke="#C8D8E0" stroke-width="3" fill="none" opacity="0.5"/>' for x in range(0, 1280, 90))
        + f'<text x="1240" y="150" font-family="Anton" font-size="118" fill="{CREAM}" text-anchor="end" stroke="#0A0E12" stroke-width="10" paint-order="stroke">SANK IN</text>'
        + f'<text x="1240" y="280" font-family="Anton" font-size="118" fill="#FFC94A" text-anchor="end" stroke="#0A0E12" stroke-width="10" paint-order="stroke">20 MINUTES</text>'
        + f'<rect x="1060" y="320" width="180" height="66" rx="12" fill="{RED}"/><text x="1150" y="368" font-family="Anton" font-size="46" fill="{CREAM}" text-anchor="middle">1628</text>')
save("thumb", body, w=W2, h=H2, defs=grad("s", [(0, "#4A5868", 1), (1, "#B8BEC4", 1)]))
shutil.copy("ep3/layers/thumb.png", "out/Thumbnail_Vasa.png")
