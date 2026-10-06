"""Genera Barbaroot: hacker hipster calvo con barba larga. Bundle .codex-pet para Orca."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, S = 48, 52, 4
COLS, ROWS = 8, 9

SKIN = (238, 192, 156, 255)
SKIN_SH = (212, 158, 122, 255)
SHINE = (255, 236, 215, 255)
BEARD = (34, 32, 36, 255)
BEARD_DK = (14, 13, 16, 255)
MUST = (52, 50, 56, 255)
GREY_HAIR = (196, 198, 204, 255)
BEARD_HI = (74, 74, 82, 255)
LIP = (205, 120, 115, 255)
HOOD = (176, 44, 44, 255)
HOOD_HI = (40, 34, 38, 255)
JEANS = (58, 92, 150, 255)
JEANS_HI = (96, 132, 190, 255)
SHOE = (240, 240, 240, 255)
SOCK = (230, 80, 70, 255)
FRAME = (20, 20, 24, 255)
LENS = (205, 225, 240, 255)
OUT = (12, 10, 14, 255)
GREEN = (60, 230, 120, 255)
BLUE = (18, 115, 235, 255)
BLUE_HI = (110, 180, 255, 255)
PINK = (255, 130, 165, 255)
RED = (235, 60, 50, 255)
YELLOW = (255, 205, 50, 255)
WHITE = (255, 255, 255, 255)
GREY = (170, 175, 190, 255)
CUP = (245, 238, 225, 255)
CUP_BAND = (150, 100, 60, 255)
SCREEN = (14, 20, 28, 255)
CLEAR = (0, 0, 0, 0)


def outline(layer):
    a = layer.getchannel("A").point(lambda v: 255 if v else 0)
    ring = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(3)), a)
    base = Image.new("RGBA", layer.size, CLEAR)
    base.paste(Image.new("RGBA", layer.size, OUT), mask=ring)
    base.alpha_composite(layer)
    return base


def new():
    return Image.new("RGBA", (W, H), CLEAR)


def arm(d, sh, hand, cup=False):
    d.line([sh, hand], fill=HOOD, width=4)
    hx, hy = hand
    d.rectangle((hx - 1, hy - 1, hx + 1, hy + 1), fill=SKIN)
    if cup:
        d.rectangle((hx - 2, hy - 6, hx + 2, hy), fill=CUP)
        d.rectangle((hx - 2, hy - 4, hx + 2, hy - 3), fill=CUP_BAND)
        d.rectangle((hx - 3, hy - 7, hx + 3, hy - 6), fill=(60, 50, 45, 255))


def hacker(eye="open", mouth="smile", larm=None, rarm=None, legs=(0, 0), lens=None,
           cup=False, tint=None, look=0, brows="normal", sway=0, cracked=False):
    """Vista frontal. larm/rarm = posición de la mano (lado izquierdo/derecho de la imagen)."""
    L = new(); d = ImageDraw.Draw(L)
    # piernas (vaqueros pitillo remangados + calcetín + zapatilla)
    for i, x in enumerate((18, 25)):
        up = legs[i]
        d.rectangle((x, 41, x + 4, 46 - up), fill=JEANS)
        d.line((x + 1, 42, x + 1, 45 - up), fill=JEANS_HI)
        d.rectangle((x, 46 - up, x + 4, 46 - up), fill=JEANS_HI)  # dobladillo
        d.rectangle((x, 47 - up, x + 4, 47 - up), fill=SOCK)
        d.rectangle((x - 1, 48 - up, x + 5, 50 - up), fill=SHOE)
        d.line((x - 1, 50 - up, x + 5, 50 - up), fill=(190, 190, 195, 255))
    # torso: sudadera con capucha
    d.rounded_rectangle((14, 25, 34, 42), 4, fill=HOOD)
    d.rectangle((15, 39, 33, 42), fill=HOOD_HI)  # cintura
    d.ellipse((13, 22, 35, 30), fill=HOOD_HI)   # capucha tras el cuello
    d.ellipse((15, 23, 33, 29), fill=HOOD)
    la = larm or (13, 38); ra = rarm or (35, 38)
    back = new(); bd = ImageDraw.Draw(back)
    arm(bd, (16, 28), la, cup=cup == "l")
    arm(bd, (32, 28), ra, cup=cup == "r")
    # cabeza calva
    d.ellipse((12, 13, 16, 19), fill=SKIN); d.ellipse((32, 13, 36, 19), fill=SKIN)  # orejas
    d.ellipse((14, 2, 34, 24), fill=SKIN)
    d.arc((16, 4, 32, 20), 200, 250, fill=SHINE, width=2)   # brillo de la calva
    d.point((20, 5), fill=WHITE)
    # gafas de pasta
    lc = lens or LENS
    for x in (16, 25):
        d.rectangle((x, 11, x + 6, 16), fill=FRAME)
        d.rectangle((x + 1, 12, x + 5, 15), fill=lc)
    d.line((23, 12, 24, 12), fill=FRAME)
    d.line((14, 12, 16, 12), fill=FRAME); d.line((32, 12, 34, 12), fill=FRAME)
    # ojos
    for x in (19, 28):
        ex = x + look
        if eye == "open":
            d.rectangle((ex - 1, 13, ex, 14), fill=OUT)
        elif eye == "closed":
            d.line((ex - 2, 14, ex + 1, 14), fill=OUT)
        elif eye == "happy":
            d.line((ex - 2, 14, ex - 1, 13), fill=OUT); d.line((ex - 1, 13, ex + 1, 14), fill=OUT)
        elif eye == "x":
            d.line((ex - 2, 12, ex + 1, 15), fill=OUT); d.line((ex - 2, 15, ex + 1, 12), fill=OUT)
        elif eye == "up":
            d.rectangle((ex - 1, 12, ex, 13), fill=OUT)
        elif eye == "glow":
            d.rectangle((ex - 1, 13, ex, 14), fill=(20, 90, 40, 255))
    if cracked:
        d.line((26, 11, 28, 14), fill=WHITE); d.line((28, 14, 27, 16), fill=WHITE); d.line((28, 14, 31, 15), fill=WHITE)
    # cejas
    if brows == "angry":
        d.line((16, 8, 21, 10), fill=BEARD_DK, width=1); d.line((27, 10, 32, 8), fill=BEARD_DK, width=1)
    elif brows == "up":
        d.line((16, 8, 21, 7), fill=BEARD_DK); d.line((27, 7, 32, 8), fill=BEARD_DK)
    else:
        d.line((16, 9, 21, 9), fill=BEARD_DK); d.line((27, 9, 32, 9), fill=BEARD_DK)
    # nariz
    d.rectangle((23, 15, 25, 18), fill=SKIN_SH)
    # barba larga (con vaivén)
    s = sway
    beard = [(14, 15), (16, 19), (19, 21), (29, 21), (32, 19), (34, 15), (35, 22), (33, 30),
             (29 + s, 37), (25 + s, 42), (23 + s, 42), (19 + s, 37), (15, 30), (13, 22)]
    d.polygon(beard, fill=BEARD)
    for x0, y0, x1, y1 in ((17, 24, 19 + s, 33), (24, 25, 24 + s, 39), (31, 24, 29 + s, 33), (21, 28, 22 + s, 37), (27, 28, 26 + s, 37)):
        d.line((x0, y0, x1, y1), fill=BEARD_DK)
    d.line((20, 23, 21 + s, 30), fill=BEARD_HI); d.line((28, 23, 27 + s, 30), fill=BEARD_HI)
    # canas: mechones grises en la barbilla y laterales
    d.line((24, 29, 24 + s, 36), fill=GREY_HAIR)
    d.line((15, 18, 16, 24), fill=BEARD_HI); d.line((33, 18, 32, 24), fill=BEARD_HI)
    for px, py in ((18, 27), (30, 26), (21, 33), (28, 32), (16, 21), (32, 21)):
        d.point((px + (s if py > 30 else 0), py), fill=GREY_HAIR)
    # bigote + boca
    d.polygon([(18, 20), (24, 18), (30, 20), (28, 22), (24, 20), (20, 22)], fill=MUST)
    d.point((21, 20), fill=GREY_HAIR); d.point((27, 20), fill=GREY_HAIR)
    if mouth == "smile":
        d.line([(21, 23), (24, 24), (27, 23)], fill=LIP)
    elif mouth == "open":
        d.rectangle((22, 22, 26, 25), fill=LIP); d.rectangle((23, 23, 25, 24), fill=(90, 30, 35, 255)); d.line((23, 25, 25, 25), fill=PINK)
    elif mouth == "frown":
        d.line([(21, 24), (24, 23), (27, 24)], fill=LIP)
    elif mouth == "flat":
        d.line((22, 23, 26, 23), fill=LIP)
    elif mouth == "sip":
        d.rectangle((23, 22, 25, 23), fill=LIP)
    L.alpha_composite(back)
    if tint:
        over = Image.new("RGBA", (W, H), tint)
        L = Image.composite(Image.blend(L, over, 0.35), L, L.getchannel("A"))
    return outline(L)


def place(fr, layer, dx=0, dy=0):
    x0, y0 = max(0, -dx), max(0, -dy)
    fr.alpha_composite(layer.crop((x0, y0, W, H)), (max(0, dx), max(0, dy)))


def bubble(fr, box):
    lay = new(); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, 3, fill=WHITE)
    x0, y0, x1, y1 = box
    d.polygon([(x0 + 2, y1), (x0 + 5, y1), (x0 - 1, y1 + 3)], fill=WHITE)
    fr.alpha_composite(outline(lay))
    return ImageDraw.Draw(fr)


# ---------- animaciones ----------
def idle():
    out = []
    for i in range(6):
        fr = new()
        sip = i in (3, 4)
        h = hacker(eye="closed" if i in (2, 4) else "open", mouth="sip" if sip else "smile",
                   rarm=(30, 23) if sip else (36, 37), cup="r", sway=[0, 0, 1, 0, 0, -1][i])
        place(fr, h, 0, [0, -1, 0, 0, 0, -1][i])
        d = ImageDraw.Draw(fr)
        if i in (0, 1, 5):  # vapor del café
            for k in range(2):
                y = 26 - k * 3 - (i % 2)
                d.point((35 + (k + i) % 2, y), fill=(220, 220, 230, 200))
        out.append(fr)
    return out


def walk():
    out = []
    for i in range(8):
        fr = new()
        ph = math.sin(i / 8 * 2 * math.pi)
        legs = (2, 0) if ph > 0.3 else ((0, 2) if ph < -0.3 else (0, 0))
        sw = round(ph * 3)
        h = hacker(look=1, larm=(13 + sw, 37), rarm=(35 + sw, 37), legs=legs, sway=-round(ph))
        place(fr, h, 1, -1 if abs(ph) < 0.3 else 0)
        d = ImageDraw.Draw(fr)
        off = i % 4
        for y, ln in ((30, 3), (36, 4), (44, 2)):
            d.line((max(0, 6 - off - ln), y, 6 - off, y), fill=BLUE_HI)
        out.append(fr)
    return out


def wave():
    out = []
    for i in range(4):
        fr = new()
        h = hacker(eye="happy", mouth="open" if i % 2 else "smile", rarm=[(39, 18), (37, 16), (39, 18), (41, 17)][i], brows="up")
        place(fr, h)
        d = ImageDraw.Draw(fr)
        hy = 5 - i
        d.polygon([(38, hy + 1), (40, hy - 1), (42, hy + 1), (44, hy - 1), (46, hy + 1), (42, hy + 5)], fill=PINK)
        out.append(fr)
    return out


def jump():
    out = []
    dys = [3, -3, -6, -3, 0]
    for i in range(5):
        fr = new()
        up = i in (1, 2, 3)
        h = hacker(eye="happy" if up else "open", mouth="open" if i == 2 else "smile",
                   larm=(9, 18) if up else (13, 38), rarm=(39, 18) if up else (35, 38),
                   legs=(2, 2) if up else (0, 0), sway=[0, 2, 0, -2, 0][i], brows="up" if up else "normal")
        if i == 0:
            h = h.resize((W, H - 3), Image.NEAREST); place(fr, h, 0, 3)
        else:
            place(fr, h, 0, dys[i])
        d = ImageDraw.Draw(fr)
        if i == 2:
            for x, y in ((5, 8), (43, 10), (40, 3)):
                for p in ((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    d.point(p, fill=YELLOW)
        out.append(fr)
    return out


def failed():
    out = []
    for i in range(8):
        fr = new()
        dx = [0, 1, -1, 1, -1, 0, 0, 0][i]
        h = hacker(eye="x", mouth="frown", brows="angry", cracked=True, lens=(255, 200, 200, 255),
                   larm=(15, 7), rarm=(33, 7), sway=dx, tint=RED if i % 2 == 0 else None)
        place(fr, h, dx, 1)
        d = ImageDraw.Draw(fr)
        if i % 2 == 0:
            d.rectangle((41, 2, 44, 10), fill=RED); d.rectangle((41, 12, 44, 14), fill=RED)
        for k in range(2):
            sy = 8 - ((i + k * 4) % 8)
            d.ellipse((4 + k * 4, sy, 7 + k * 4, sy + 3), fill=GREY)
        out.append(fr)
    return out


def waiting():
    out = []
    for i in range(6):
        fr = new()
        h = hacker(eye="up", mouth="flat", larm=(28, 32), rarm=(20, 32), legs=(1 if i % 2 else 0, 0), look=1)
        place(fr, h, -2, 2)
        d = bubble(fr, (34, 1, 47, 10))
        for k in range(3):
            d.rectangle((36 + k * 4, 5, 37 + k * 4, 6), fill=BLUE if k < i % 4 else (210, 215, 225, 255))
        out.append(fr)
    return out


def working():
    out = []
    for i in range(6):
        fr = new()
        h = hacker(eye="glow", lens=(150, 255, 180, 255), mouth="smile", brows="angry",
                   larm=(17 + (i % 2), 39), rarm=(31 - (i % 2), 39), sway=0)
        place(fr, h, 0, 0)
        lay = new(); d = ImageDraw.Draw(lay)
        d.rectangle((14, 32, 34, 44), fill=(70, 74, 86, 255))       # tapa del portátil (vista trasera)
        d.rectangle((15, 33, 33, 43), fill=(92, 98, 112, 255))
        # pegatinas hipster
        d.ellipse((17, 35, 21, 39), fill=BLUE); d.rectangle((24, 34, 28, 37), fill=YELLOW)
        d.polygon([(29, 42), (32, 38), (32, 42)], fill=PINK)
        d.rectangle((22, 39, 26, 41), fill=GREEN)
        d.rectangle((12, 44, 36, 46), fill=(150, 156, 170, 255))
        fr.alpha_composite(outline(lay))
        d = ImageDraw.Draw(fr)
        # bits flotando
        for k, ch in enumerate("1010"):
            y = 10 - ((i * 2 + k * 3) % 10)
            x = [3, 8, 40, 44][k]
            if ch == "1":
                d.line((x, y, x, y + 3), fill=GREEN)
            else:
                d.rectangle((x - 1, y, x + 1, y + 3), outline=GREEN)
        out.append(fr)
    return out


def review():
    out = []
    for i in range(6):
        fr = new()
        cx = [30, 32, 32, 30, 29, 29][i]; cy = 14
        h = hacker(eye="open", look=1 if i in (1, 2) else 0, mouth="open" if i >= 4 else "flat",
                   brows="up" if i >= 4 else "normal", rarm=(cx + 5, cy + 7))
        place(fr, h)
        lay = new(); d = ImageDraw.Draw(lay)
        d.line((cx + 3, cy + 4, cx + 6, cy + 8), fill=(90, 60, 30, 255), width=2)
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(170, 225, 255, 110), outline=BLUE, width=2)
        d.point((cx - 2, cy - 2), fill=WHITE); d.point((cx - 1, cy - 3), fill=WHITE)
        fr.alpha_composite(outline(lay))
        if i >= 4:
            d2 = bubble(fr, (36, 0, 47, 9))
            d2.line([(38, 4), (40, 6), (44, 2)], fill=(30, 180, 90, 255), width=2)
        out.append(fr)
    return out


ROW_FNS = [
    ("idle", idle), ("running-right", walk), ("running-left", lambda: [f.transpose(Image.FLIP_LEFT_RIGHT) for f in walk()]),
    ("waving", wave), ("jumping", jump), ("failed", failed), ("waiting", waiting), ("running", working), ("review", review),
]


def main(out_dir, preview):
    sheet = Image.new("RGBA", (COLS * W * S, ROWS * H * S), CLEAR)
    for r, (name, fn) in enumerate(ROW_FNS):
        for c, f in enumerate(fn()):
            sheet.paste(f.resize((W * S, H * S), Image.NEAREST), (c * W * S, r * H * S))
    os.makedirs(out_dir, exist_ok=True)
    sheet.save(os.path.join(out_dir, "spritesheet.webp"), lossless=True, quality=100)
    with open(os.path.join(out_dir, "pet.json"), "w") as fh:
        json.dump({"id": "barbaroot", "displayName": "Barbaroot",
                   "description": "Hacker hipster calvo de barba larga: café de especialidad, gafas de pasta, portátil con pegatinas y sudo en las venas."},
                  fh, indent=2, ensure_ascii=False)
    prev = Image.new("RGBA", sheet.size, (40, 44, 52, 255)); prev.alpha_composite(sheet)
    prev.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.NEAREST).save(preview)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
