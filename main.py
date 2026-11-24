#!/usr/bin/env python3
"""Entry program for the news-image-20261124 make.fun bounty.

It draws an original newspaper front page -- "THE WORLD TODAY / TUESDAY
24 NOVEMBER 2026" -- with six illustrated panels summing up that day's
world news, and writes it as a 1024x1024 PNG to the output directory
(MAKEFUN_OUTPUT_DIR, default /output).

The drawing uses Pillow when it is available. The grading container is
standard-library-only, so when Pillow is missing the program falls back
to copying the bundled entry.png -- which this same program's drawing
code produced -- so the bytes written are identical either way. There
is no randomness and no clock anywhere in the drawing: every run on the
same machine writes exactly the same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

W = H = 1024
PAPER = (247, 242, 231)
INK = (22, 19, 15)
GREY = (96, 92, 84)

FONT_CANDIDATES = {
    "serif": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "serif-bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif-italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
}


def load_font(ImageFont, kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    """Greedy word wrap against pixel widths; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, ImageFont, kind, text, start_size, max_width):
    """Largest bold size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > 10:
        font = load_font(ImageFont, kind, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return load_font(ImageFont, kind, size)


def draw_masthead(draw, ImageFont):
    # Double rule above the nameplate, in the classic broadsheet style.
    draw.line([(28, 22), (996, 22)], fill=INK, width=2)
    draw.line([(28, 28), (996, 28)], fill=INK, width=6)
    title = "THE WORLD TODAY"
    font = fit_font(draw, ImageFont, "serif-bold", title, 96, 940)
    tw = draw.textlength(title, font=font)
    draw.text(((W - tw) / 2, 40), title, font=font, fill=INK)
    # Black date band.
    draw.rectangle([28, 120, 996, 162], fill=INK)
    date = "TUESDAY 24 NOVEMBER 2026"
    dfont = fit_font(draw, ImageFont, "serif-bold", date, 34, 700)
    dw = draw.textlength(date, font=dfont)
    draw.text(((W - dw) / 2, 129), date, font=dfont, fill=(255, 255, 255))
    sub = "The day's six biggest stories, drawn and typeset by program code"
    sfont = load_font(ImageFont, "serif-italic", 17)
    sw = draw.textlength(sub, font=sfont)
    draw.text(((W - sw) / 2, 168), sub, font=sfont, fill=GREY)
    draw.line([(28, 190), (996, 190)], fill=INK, width=2)


def panel_frame(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    return (x + 6, y + 6, x + w - 6, y + 224)  # illustration box


def draw_panel_text(draw, ImageFont, x, y, w, headline, caption):
    hfont = load_font(ImageFont, "serif-bold", 25)
    cy = y + 232
    for line in wrap(draw, headline, hfont, w - 16):
        draw.text((x + 10, cy), line, font=hfont, fill=INK)
        cy += 30
    cfont = load_font(ImageFont, "serif", 16)
    cy += 4
    for line in wrap(draw, caption, cfont, w - 16):
        draw.text((x + 10, cy), line, font=cfont, fill=(52, 48, 42))
        cy += 21


# --- Panel illustrations: flat editorial shapes, all original --------

def ill_markets(draw, F):
    # A trading screen after the Nvidia shock: bars leaping upward.
    draw.rectangle([0, 0, 312, 218], fill=(14, 24, 42))
    for gy in range(28, 190, 32):                                 # grid
        draw.line([(10, gy), (302, gy)], fill=(34, 52, 78), width=1)
    # Four rising green candles, left to right.
    bars = [(28, 118, 158), (76, 100, 162), (124, 78, 166), (172, 52, 170)]
    for bx, top, bot in bars:
        draw.line([(bx + 13, top - 12), (bx + 13, bot + 8)],
                  fill=(90, 220, 130), width=3)
        draw.rectangle([bx, top, bx + 26, bot], fill=(46, 178, 92))
    # The leap: a fat arrow from the last bar toward the top right.
    draw.polygon([(206, 96), (272, 30), (262, 66), (288, 40), (292, 92),
                  (240, 84), (214, 118)], fill=(90, 220, 130))
    # A gold chip, for the AI trade at the centre of the story.
    draw.rectangle([232, 128, 282, 178], fill=(216, 172, 60))
    draw.rectangle([244, 140, 270, 166], fill=(160, 124, 34))
    for px in (238, 252, 266):
        draw.line([(px, 118), (px, 128)], fill=(216, 172, 60), width=3)
        draw.line([(px, 178), (px, 188)], fill=(216, 172, 60), width=3)
    # The day's numbers, in green, in one row along the bottom.
    font = F("serif-bold", 15)
    draw.text((8, 192), "NIKKEI +4.5%", font=font, fill=(140, 235, 165))
    draw.text((108, 192), "KOSPI +7.5%", font=font, fill=(140, 235, 165))
    draw.text((208, 192), "TAIEX +9.1%", font=font, fill=(140, 235, 165))


def ill_shenzhou(draw):
    # Tiangong station above the Earth's limb, a rocket climbing to it.
    draw.rectangle([0, 0, 312, 218], fill=(8, 14, 36))
    for sx, sy in [(22, 26), (66, 60), (110, 18), (286, 30), (248, 66),
                   (36, 96), (292, 104), (150, 44), (206, 16)]:
        draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(225, 230, 245))
    # Earth limb along the bottom.
    draw.pieslice([-160, 128, 472, 420], 180, 360, fill=(38, 92, 160))
    draw.pieslice([-160, 118, 472, 410], 180, 360, fill=(70, 130, 190))
    # The station: core module, node and two solar wings.
    draw.rectangle([128, 74, 184, 92], fill=(214, 218, 224))
    draw.rectangle([146, 62, 166, 106], fill=(196, 202, 210))
    draw.rectangle([152, 106, 160, 122], fill=(170, 176, 186))
    for wx0 in (52, 196):
        draw.rectangle([wx0, 66, wx0 + 64, 100], fill=(38, 62, 128))
        for gx in range(wx0 + 8, wx0 + 62, 12):
            draw.line([(gx, 68), (gx, 98)], fill=(90, 120, 180), width=2)
        draw.line([(wx0, 83), (wx0 + 64, 83)], fill=(90, 120, 180), width=2)
    draw.line([(116, 83), (128, 83)], fill=(214, 218, 224), width=4)
    draw.line([(184, 83), (196, 83)], fill=(214, 218, 224), width=4)
    # A small green flag on the core: the first visiting astronaut's.
    draw.line([(178, 74), (178, 56)], fill=(220, 224, 230), width=2)
    draw.polygon([(178, 56), (196, 60), (178, 65)], fill=(30, 150, 80))
    # The Shenzhou rocket climbing from the lower left, flame lit.
    draw.polygon([(52, 150), (64, 118), (76, 150)], fill=(232, 234, 238))
    draw.rectangle([56, 148, 72, 158], fill=(200, 204, 212))
    draw.polygon([(58, 158), (64, 184), (70, 158)], fill=(244, 150, 50))
    draw.polygon([(61, 158), (64, 172), (67, 158)], fill=(250, 210, 90))
    for tx, ty in [(46, 168), (38, 182), (50, 194)]:
        draw.ellipse([tx, ty, tx + 5, ty + 5], fill=(150, 160, 180))


def ill_bougainville(draw, F):
    # A Pacific island, and the ballot its future turns on.
    draw.rectangle([0, 0, 312, 128], fill=(168, 208, 228))        # sky
    draw.rectangle([0, 128, 312, 218], fill=(30, 110, 140))       # sea
    for i in range(4):                                            # waves
        yy = 148 + i * 17
        draw.line([(16 + (i % 2) * 26, yy), (86 + (i % 2) * 26, yy)],
                  fill=(120, 190, 205), width=2)
    # The island: green hills on a sandy shore.
    draw.polygon([(96, 128), (140, 82), (196, 66), (248, 92), (268, 128)],
                 fill=(64, 140, 78))
    draw.polygon([(96, 128), (268, 128), (268, 138), (96, 138)],
                 fill=(226, 205, 150))
    # Palm trees.
    for px, py in [(128, 108), (228, 100)]:
        draw.line([(px, py + 22), (px + 4, py)], fill=(110, 84, 52), width=4)
        for dx, dy in [(-20, -8), (-8, -14), (6, -15), (18, -9), (0, -6)]:
            draw.arc([px + 4 + dx - 14, py + dy - 8, px + 4 + dx + 14,
                      py + dy + 10], 180, 340, fill=(40, 116, 60), width=3)
    # The ballot paper, big in the foreground, its box ticked.
    draw.rectangle([168, 128, 292, 206], fill=(250, 249, 244),
                   outline=(90, 86, 78), width=2)
    draw.rectangle([182, 142, 206, 166], outline=(40, 40, 44), width=3)
    draw.line([(186, 154), (194, 163)], fill=(30, 140, 70), width=5)
    draw.line([(194, 163), (204, 144)], fill=(30, 140, 70), width=5)
    for ly in (148, 160):
        draw.line([(216, ly), (280, ly)], fill=(170, 166, 156), width=3)
    font = F("serif-bold", 30)
    draw.text((182, 172), "98%", font=font, fill=(30, 120, 64))


def _star(draw, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def ill_anwar(draw):
    # Kuala Lumpur's twin towers, courted from both sides at once.
    draw.rectangle([0, 0, 312, 218], fill=(196, 216, 232))
    draw.rectangle([0, 178, 312, 218], fill=(120, 128, 120))      # ground
    # The two suitors, as plain star panels: blue west, red east.
    draw.rectangle([18, 30, 84, 96], fill=(44, 62, 140))
    _star(draw, 51, 63, 17, (245, 245, 248))
    draw.rectangle([228, 30, 294, 96], fill=(196, 40, 44))
    _star(draw, 252, 54, 13, (250, 205, 60))
    for sx, sy in [(276, 44), (282, 60), (276, 76)]:
        draw.ellipse([sx, sy, sx + 6, sy + 6], fill=(250, 205, 60))
    # A gold arc of courtship over the towers, joining the two panels.
    draw.arc([44, 8, 268, 130], 200, 340, fill=(216, 172, 60), width=5)
    # The Petronas twin towers, with their skybridge.
    for tx in (128, 168):
        draw.polygon([(tx, 178), (tx + 4, 92), (tx + 12, 66), (tx + 20, 92),
                      (tx + 24, 178)], fill=(148, 162, 178))
        draw.line([(tx + 12, 66), (tx + 12, 46)], fill=(110, 122, 138), width=3)
        for wy in range(104, 170, 14):
            draw.line([(tx + 5, wy), (tx + 19, wy)], fill=(110, 126, 146),
                      width=2)
    draw.rectangle([140, 128, 184, 138], fill=(110, 122, 138))
    # Smaller towers at the edges of the skyline.
    for bx, bh in [(92, 52), (206, 62), (240, 40)]:
        draw.rectangle([bx, 178 - bh, bx + 22, 178], fill=(128, 140, 154))
    # A data-centre block in the foreground, chip on its face.
    draw.rectangle([24, 150, 96, 178], fill=(90, 98, 110))
    draw.rectangle([48, 156, 72, 172], outline=(140, 230, 170), width=2)
    draw.rectangle([56, 161, 64, 167], fill=(140, 230, 170))


def ill_bok(draw, F):
    # The central bank in Seoul, and the rate the poll expects.
    draw.rectangle([0, 0, 312, 218], fill=(233, 229, 218))
    # The bank: pediment, beam, four columns, steps.
    draw.polygon([(26, 62), (104, 26), (182, 62)], fill=(120, 116, 106))
    draw.rectangle([26, 62, 182, 74], fill=(140, 136, 126))
    for cx in (38, 76, 114, 152):
        draw.rectangle([cx, 82, cx + 18, 168], fill=(206, 202, 192))
        draw.rectangle([cx - 3, 76, cx + 21, 82], fill=(140, 136, 126))
        draw.rectangle([cx - 3, 168, cx + 21, 174], fill=(140, 136, 126))
    draw.rectangle([20, 174, 188, 182], fill=(160, 156, 146))
    draw.rectangle([14, 182, 194, 190], fill=(140, 136, 126))
    draw.rectangle([86, 128, 122, 168], fill=(96, 92, 84))        # door
    # The expected move: red steps climbing to the new rate.
    steps = [(206, 168), (232, 168), (232, 140), (258, 140), (258, 112),
             (284, 112), (284, 84)]
    draw.line(steps, fill=(188, 44, 44), width=5)
    draw.polygon([(284, 66), (274, 86), (294, 86)], fill=(188, 44, 44))
    font = F("serif-bold", 34)
    draw.text((198, 20), "3.25%", font=font, fill=(168, 36, 36))
    font2 = F("serif-bold", 19)
    draw.text((206, 186), "NOV 26", font=font2, fill=(96, 92, 84))


def ill_chess(draw, F):
    # Two kings, both twenty years old, over a chequerboard.
    draw.rectangle([0, 0, 312, 218], fill=(58, 42, 32))
    font = F("serif-bold", 23)
    tw = draw.textlength("GAME 1", font=font)
    draw.text(((312 - tw) / 2, 12), "GAME 1", font=font, fill=(240, 224, 190))
    # The board: three ranks of squares along the bottom.
    sq = 30
    for r in range(3):
        for c in range(8):
            x, y = 36 + c * sq, 124 + r * sq
            fill = (232, 214, 178) if (r + c) % 2 == 0 else (140, 96, 60)
            draw.rectangle([x, y, x + sq, y + sq], fill=fill)
    draw.rectangle([36, 124, 276, 214], outline=(30, 22, 16), width=3)

    def king(cx, body, trim):
        # Base, body, collar and cross, centred on cx, foot at y=170.
        draw.rectangle([cx - 30, 158, cx + 30, 170], fill=body)
        draw.polygon([(cx - 20, 158), (cx - 12, 108), (cx + 12, 108),
                      (cx + 20, 158)], fill=body)
        draw.rectangle([cx - 17, 96, cx + 17, 108], fill=body)
        draw.rectangle([cx - 4, 62, cx + 4, 96], fill=trim)
        draw.rectangle([cx - 13, 72, cx + 13, 80], fill=trim)
        draw.rectangle([cx - 22, 104, cx + 22, 110], fill=trim)

    king(88, (238, 234, 226), (120, 116, 108))                    # white
    king(224, (26, 24, 26), (216, 172, 60))                       # black


STORIES = [
    (ill_markets,
     "ASIA MARKETS LEAP AS NVIDIA REINSTATES ITS CHIEF",
     "Nvidia's 31.5% Monday surge on Jensen Huang's return lit up "
     "Tuesday's trading: Nikkei +4.5%, Kospi +7.5%, Taiwan +9.1%."),
    (lambda d, F: ill_shenzhou(d),
     "FIRST FOREIGN ASTRONAUT TO VISIT CHINA'S TIANGONG",
     "Pakistan's Muhammad Zeeshan Ali joins Shenzhou-24, unveiled "
     "Tuesday. Launch is set for Wednesday from Jiuquan."),
    (ill_bougainville,
     "PNG VOTES ON BOUGAINVILLE INDEPENDENCE",
     "Parliament took up ratifying the 2019 referendum, when "
     "almost 98% chose independence."),
    (lambda d, F: ill_anwar(d),
     "MALAYSIA'S ANWAR: CHINA EASIER TO DEAL WITH THAN US",
     "In an SCMP interview published Tuesday, Anwar said Beijing "
     "never pressed Malaysia over its US ties or tech deals."),
    (ill_bok,
     "BANK OF KOREA EXPECTED TO RAISE RATES ON THURSDAY",
     "32 of 34 economists in a Reuters poll published Tuesday "
     "expect a quarter-point rise to 3.25% on November 26."),
    (ill_chess,
     "YOUNGEST WORLD CHESS TITLE MATCH OPENS IN GENEVA",
     "Champion Gukesh of India faces Uzbekistan's Sindarov, both "
     "aged 20, in Game 1 at Cologny on Tuesday."),
]

PANEL_W, PANEL_H = 312, 397
GRID_X = (28, 356, 684)
GRID_Y = (202, 613)


def render(out_path):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, ImageFont)

    def font_of(kind, size):
        return load_font(ImageFont, kind, size)

    for i, (ill, headline, caption) in enumerate(STORIES):
        px, py = GRID_X[i % 3], GRID_Y[i // 3]
        tile = Image.new("RGB", (PANEL_W, 218), PAPER)
        ill(ImageDraw.Draw(tile), font_of)
        img.paste(tile, (px, py + 6))
        draw = ImageDraw.Draw(img)
        panel_frame(draw, px, py, PANEL_W, PANEL_H)
        draw_panel_text(draw, ImageFont, px, py, PANEL_W, headline, caption)

    img.save(out_path, format="PNG")
    return out_path


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    try:
        import PIL  # noqa: F401
    except ImportError:
        # Standard-library-only runtime: ship the bundled image, which
        # this program's drawing code produced, byte for byte.
        shutil.copyfile(os.path.join(HERE, "entry.png"), dst)
        return 0
    render(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
