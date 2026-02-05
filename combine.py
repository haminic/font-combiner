import math

import fontforge
import psMat

THAI_FONT_DIR = "fonts/donor/"
ENG_FONT_DIR = "fonts/source/"
OUT_DIR = "out/"

WIDTH_THRESHOLD = 50

# SETTINGS

THAI_FONT_FILE = "SOV_monomon-hinted.ttf"
ENG_FONT_FILE = "MapleMono-NF-BoldItalic.ttf"
OUT_FILE = "MapleMonomon-NF-BoldItalic.ttf"

NEW_FAMILY = "Maple Monomon NF"
NEW_FULL = "Maple Monomon NF BoldItalic"
NEW_PSNAME = "MapleMonomon-NF-BoldItalic"

UNIFORM_SCALE = 600 / 560
Y_SCALE = 550 / 536

EMBOLDEN_STRENGTH = 42
ITALIC_ANGLE = -10

MONO_WIDTH = 600

if __name__ == "__main__":
    thai = fontforge.open(THAI_FONT_DIR + THAI_FONT_FILE)
    eng = fontforge.open(ENG_FONT_DIR + ENG_FONT_FILE)

    # === NORMALIZE ===

    scale_to_eng = eng.em / thai.em

    thai.selection.all()
    thai.transform(psMat.scale(scale_to_eng))
    thai.em = eng.em

    # === SCALE ===

    thai.selection.all()
    thai.transform(psMat.scale(UNIFORM_SCALE))

    thai.transform(psMat.scale(1.0, Y_SCALE))

    # === ADJUST WEIGHT ===

    if EMBOLDEN_STRENGTH != 0:
        for g in thai.glyphs():
            xmin0, ymin0, xmax0, ymax0 = g.boundingBox()
            h0 = ymax0 - ymin0
            cy0 = (ymin0 + ymax0) / 2

            g.changeWeight(EMBOLDEN_STRENGTH)

            xmin1, ymin1, xmax1, ymax1 = g.boundingBox()
            h1 = ymax1 - ymin1
            cy1 = (ymin1 + ymax1) / 2

            # --- Fix skewing artifacts ---
            # Y scale
            if h1 == 0:
                continue
            sy = h0 / h1
            g.transform(psMat.scale(1, sy))

            # Shift
            xmin2, ymin2, xmax2, ymax2 = g.boundingBox()
            cy2 = (ymin2 + ymax2) / 2

            dy = cy0 - cy2
            g.transform(psMat.translate(0, dy))

    # === APPLY FAKE ITALIC ===

    if ITALIC_ANGLE != 0:
        skew_matrix = psMat.skew(math.radians(-ITALIC_ANGLE))

        for g in thai.glyphs():
            xmin0, ymin0, xmax0, ymax0 = g.boundingBox()
            g.transform(skew_matrix)
            xmin1, ymin1, xmax1, ymax1 = g.boundingBox()

            # Fix offset
            dx = ((xmin0 + xmax0) - (xmin1 + xmax1)) / 2
            g.transform(psMat.translate(dx, 0))

    # === WIDTH NORMALIZATION ===

    for g in thai.glyphs():
        if g.width < WIDTH_THRESHOLD:
            g.width = 0
        else:
            g.width = MONO_WIDTH

    # === GENERATE FONT ===

    eng.mergeFonts(thai)

    eng.familyname = NEW_FAMILY
    eng.fullname = NEW_FULL
    eng.fontname = NEW_PSNAME

    eng.appendSFNTName("English (US)", "Preferred Family", NEW_FAMILY)
    eng.appendSFNTName("English (US)", "Fullname", NEW_FULL)

    eng.generate(OUT_DIR + OUT_FILE)

    print("Done.")
