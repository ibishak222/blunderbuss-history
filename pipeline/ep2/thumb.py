import sys
sys.path.insert(0, "ep2")
from art2 import *
import shutil
W2, H2 = 1280, 720
body = (f'<rect width="{W2}" height="{H2}" fill="url(#s)"/><circle cx="330" cy="430" r="260" fill="#FFD27A"/>'
        f'<rect y="630" width="{W2}" height="90" fill="#2A1810"/>'
        + emu(250, 640, 1.25, "stand", col="#160C08")
        + soldier(1060, 640, 0.72, col="#160C08", pose="kneel", flip=True) + lewis(1000, 640, 0.8, col="#160C08", flip=True)
        + '<circle cx="830" cy="590" r="60" fill="url(#fl)"/>'
        f'<text x="1240" y="150" font-family="Anton" font-size="122" fill="{CREAM}" text-anchor="end" stroke="#0E0806" stroke-width="10" paint-order="stroke">EMUS BEAT</text>'
        f'<text x="1240" y="280" font-family="Anton" font-size="122" fill="#FFC94A" text-anchor="end" stroke="#0E0806" stroke-width="10" paint-order="stroke">THE ARMY</text>'
        f'<rect x="1060" y="320" width="180" height="66" rx="12" fill="{RED}"/><text x="1150" y="368" font-family="Anton" font-size="46" fill="{CREAM}" text-anchor="middle">1932</text>')
defs = (grad("s", [(0, "#2A1E3A", 1), (0.6, "#C8643C", 1), (1, "#F4B860", 1)])
        + '<radialGradient id="fl"><stop offset="0" stop-color="#FFF3C4"/><stop offset="0.35" stop-color="#FFB347" stop-opacity="0.9"/><stop offset="1" stop-color="#D9482B" stop-opacity="0"/></radialGradient>')
save("thumb", body, w=W2, h=H2, defs=defs)
shutil.copy("ep2/layers/thumb.png", "out/Thumbnail_EmuWar.png")
