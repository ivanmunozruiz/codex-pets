"""Genera Pikorca: bundle .codex-pet para Orca (spritesheet 8x9 de frames 192x208)."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, S = 48, 52, 4  # resolución lógica pixel-art, escalado x4 -> 192x208
COLS, ROWS = 8, 9

BODY = (28, 34, 54, 255)
BODY_HI = (52, 62, 92, 255)
BELLY = (244, 247, 252, 255)
OUT = (8, 10, 20, 255)
BLUE = (18, 115, 235, 255)      # azul Freepik
BLUE_HI = (110, 180, 255, 255)
PINK = (255, 130, 165, 255)
GREEN = (40, 200, 110, 255)
RED = (235, 60, 50, 255)
YELLOW = (255, 205, 50, 255)
WATER = (120, 205, 255, 255)
WHITE = (255, 255, 255, 255)
SCREEN = (16, 22, 34, 255)
GREY = (170, 175, 190, 255)
CLEAR = (0, 0, 0, 0)


def outline(layer):
    a = layer.getchannel("A").point(lambda v: 255 if v else 0)
    grown = a.filter(ImageFilter.MaxFilter(3))
    ring = ImageChops.subtract(grown, a)
    base = Image.new("RGBA", layer.size, CLEAR)
    base.paste(Image.new("RGBA", layer.size, OUT), mask=ring)
    base.alpha_composite(layer)
    return base


def orca(eye="open", tail=0, fin="down", mouth="smile", headset=True, tint=None, look=0):
    L = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(L)
    t = tail
    # cola + aletas caudales
    d.polygon([(13, 26), (6, 28 + t), (6, 31 + t), (13, 34)], fill=BODY)
    d.polygon([(7, 29 + t), (1, 22 + t), (4, 21 + t), (9, 28 + t)], fill=BODY)
    d.polygon([(7, 30 + t), (1, 37 + t), (4, 38 + t), (9, 31 + t)], fill=BODY)
    # aleta dorsal
    d.polygon([(18, 22), (19, 13), (21, 10), (23, 11), (28, 22)], fill=BODY)
    # cuerpo
    d.ellipse((9, 19, 42, 43), fill=BODY)
    d.arc((12, 21, 40, 41), 200, 260, fill=BODY_HI)
    # barriga (recortada al cuerpo)
    body_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(body_mask).ellipse((9, 19, 42, 43), fill=255)
    bl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(bl).ellipse((14, 31, 46, 47), fill=255)
    L.paste(Image.new("RGBA", (W, H), BELLY), mask=ImageChops.multiply(bl, body_mask))
    # mancha del ojo + ojo
    d.ellipse((28, 22, 37, 29), fill=BELLY)
    ex = 32 + look
    if eye == "open":
        d.rectangle((ex - 1, 23, ex + 2, 27), fill=OUT)
        d.rectangle((ex - 1, 23, ex, 24), fill=WHITE)
    elif eye == "closed":
        d.line((ex - 2, 26, ex + 2, 26), fill=OUT)
    elif eye == "happy":
        d.line((ex - 2, 26, ex, 24), fill=OUT); d.line((ex, 24, ex + 2, 26), fill=OUT)
    elif eye == "x":
        d.line((ex - 2, 24, ex + 2, 28), fill=OUT); d.line((ex - 2, 28, ex + 2, 24), fill=OUT)
    elif eye == "up":
        d.rectangle((ex, 22, ex + 3, 25), fill=OUT); d.point((ex, 22), fill=WHITE)
    # mofletes y boca
    d.rectangle((36, 31, 37, 31), fill=PINK)
    if mouth == "smile":
        d.line([(35, 34), (37, 35), (40, 34)], fill=OUT)
    elif mouth == "open":
        d.ellipse((36, 33, 39, 36), fill=OUT); d.point((37, 35), fill=PINK)
    elif mouth == "frown":
        d.line([(35, 35), (37, 34), (40, 35)], fill=OUT)
    elif mouth == "flat":
        d.line([(36, 34), (39, 34)], fill=OUT)
    # aleta pectoral
    fins = {
        "down": [(19, 37), (24, 37), (19, 45), (15, 43)],
        "mid": [(19, 37), (24, 37), (27, 44), (22, 45)],
        "up": [(22, 35), (26, 34), (31, 27), (28, 26)],
        "up2": [(22, 35), (26, 34), (27, 25), (24, 25)],
    }
    d.polygon(fins[fin], fill=BODY_HI)
    # auriculares de guardia
    if headset:
        d.arc((20, 15, 34, 33), 200, 330, fill=BLUE, width=2)
        d.rounded_rectangle((21, 23, 25, 29), 1, fill=BLUE)
        d.point((22, 24), fill=BLUE_HI); d.point((22, 25), fill=BLUE_HI)
        d.line([(24, 30), (27, 34), (32, 36)], fill=BLUE)
        d.rectangle((32, 35, 34, 37), fill=BLUE_HI)
    if tint:
        over = Image.new("RGBA", (W, H), tint)
        L = Image.composite(Image.blend(L, over, 0.35), L, L.getchannel("A"))
    return outline(L)


def place(frame, layer, dx=0, dy=0):
    frame.alpha_composite(layer, (dx, dy)) if dx >= 0 and dy >= 0 else frame.alpha_composite(
        layer.crop((max(0, -dx), max(0, -dy), W, H)), (max(0, dx), max(0, dy)))


def new():
    return Image.new("RGBA", (W, H), CLEAR)


def drops(d, pts, c=WATER):
    for x, y in pts:
        d.rectangle((x, y, x + 1, y + 1), fill=c)


def bubble(fr, box):
    lay = new(); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, 3, fill=WHITE)
    x0, y0, x1, y1 = box
    d.polygon([(x0 + 3, y1), (x0 + 6, y1), (x0 + 1, y1 + 3)], fill=WHITE)
    fr.alpha_composite(outline(lay))
    return ImageDraw.Draw(fr)


# ---------- animaciones (fila: frames) ----------
def idle():
    out = []
    for i in range(6):
        fr = new()
        dy = [0, -1, 0, 0, -1, 0][i]
        place(fr, orca(eye="closed" if i == 2 else "open", tail=[0, 1, 0, 0, 1, 0][i]), 0, dy)
        d = ImageDraw.Draw(fr)
        if i == 3:
            drops(d, [(21, 13 + dy), (22, 10 + dy)])
        if i == 4:
            drops(d, [(21, 11 + dy), (22, 7 + dy), (19, 5 + dy), (25, 5 + dy), (22, 3 + dy)])
        out.append(fr)
    return out


def swim():
    out = []
    for i in range(8):
        fr = new()
        t = [0, 1, 2, 1, 0, -1, -2, -1][i]
        dy = [0, -1, -1, 0, 0, 1, 1, 0][i]
        place(fr, orca(tail=t, fin="mid" if i % 4 < 2 else "down", mouth="open" if i in (2, 6) else "smile"), 3, dy)
        d = ImageDraw.Draw(fr)
        off = (i * 2) % 6
        for y, ln in ((24, 4), (30, 6), (36, 3)):
            d.line((max(0, 1 - off + 2), y + dy, 1 - off + 2 + ln, y + dy), fill=BLUE_HI)
        drops(d, [(2, 18 - (i % 4) * 3)], c=(160, 220, 255, 200))
        out.append(fr)
    return out


def wave():
    out = []
    for i in range(4):
        fr = new()
        place(fr, orca(eye="happy", fin=["up", "up2", "up", "up2"][i], mouth="open" if i % 2 else "smile"))
        d = ImageDraw.Draw(fr)
        hy = 8 - i
        d.polygon([(38, hy + 1), (40, hy - 1), (42, hy + 1), (44, hy - 1), (46, hy + 1), (42, hy + 5)], fill=PINK)
        out.append(fr)
    return out


def jump():
    out = []
    dys = [3, -4, -8, -4, 0]
    for i in range(5):
        fr = new()
        o = orca(eye="happy" if i in (1, 2, 3) else "open", tail=[0, 2, 1, -1, 0][i], fin="up" if i == 2 else "mid", mouth="open" if i == 2 else "smile")
        if i == 0:  # aplastado
            o = o.resize((W, H - 4), Image.NEAREST); place(fr, o, 0, 4)
        else:
            o = o.rotate([0, 8, 0, -8, 0][i], resample=Image.NEAREST, center=(25, 31))
            place(fr, o, 0, max(dys[i], 0)) if dys[i] >= 0 else fr.alpha_composite(o.crop((0, -dys[i], W, H)), (0, 0))
        d = ImageDraw.Draw(fr)
        if i == 2:
            for x, y in ((6, 6), (42, 10), (40, 2)):
                d.point((x, y), fill=YELLOW); d.point((x - 1, y), fill=YELLOW); d.point((x + 1, y), fill=YELLOW)
                d.point((x, y - 1), fill=YELLOW); d.point((x, y + 1), fill=YELLOW)
        if i == 4:
            drops(d, [(8, 44), (38, 44), (5, 41), (41, 41)])
        out.append(fr)
    return out


def failed():
    out = []
    for i in range(8):
        fr = new()
        dx = [0, 1, -1, 1, -1, 0, 0, 0][i]
        place(fr, orca(eye="x", mouth="frown", fin="down", tint=RED if i % 2 == 0 else None), 1 + dx, 0)
        d = ImageDraw.Draw(fr)
        if i % 2 == 0:  # alerta roja de pager
            d.rectangle((40, 3, 43, 10), fill=RED); d.rectangle((40, 12, 43, 14), fill=RED)
        for k in range(2):  # humo
            sy = 16 - ((i + k * 4) % 8) * 2
            d.ellipse((17 + k * 4, sy, 20 + k * 4, sy + 3), fill=GREY)
        out.append(fr)
    return out


def waiting():
    out = []
    for i in range(6):
        fr = new()
        place(fr, orca(eye="up", mouth="flat", fin="down", tail=0 if i % 3 else 1), -2, 2)
        d = bubble(fr, (33, 2, 46, 11))
        for k in range(3):
            c = BLUE if k <= i % 4 - 1 or i % 4 == 0 and False else (210, 215, 225, 255)
            if k < (i % 4):
                c = BLUE
            d.rectangle((35 + k * 4, 6, 36 + k * 4, 7), fill=c)
        out.append(fr)
    return out


def working():
    out = []
    for i in range(6):
        fr = new()
        place(fr, orca(eye="open", look=1, fin="mid" if i % 2 else "up", mouth="smile", tail=i % 2), -4, 0)
        lay = new(); d = ImageDraw.Draw(lay)
        d.rectangle((32, 33, 46, 43), fill=(60, 66, 80, 255))
        d.rectangle((33, 34, 45, 42), fill=SCREEN)
        d.rectangle((30, 43, 47, 45), fill=(140, 146, 160, 255))
        cols = [GREEN, BLUE_HI, YELLOW, GREEN, PINK, BLUE_HI]
        for r in range(4):
            ln = 3 + ((i + r * 3) % 6)
            d.line((34 + (r % 2), 35 + r * 2, 34 + (r % 2) + ln, 35 + r * 2), fill=cols[(i + r) % 6])
        if i % 2 == 0:
            d.point((35 + ((i * 3) % 8), 41), fill=WHITE)  # cursor
        fr.alpha_composite(outline(lay))
        # ruedita de helm (k8s) girando
        g = new(); gd = ImageDraw.Draw(g)
        cx, cy = 41, 8
        gd.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), outline=BLUE, width=2)
        for k in range(7):
            a = k * 2 * math.pi / 7 + i * 0.45
            gd.line((cx, cy, cx + round(6 * math.cos(a)), cy + round(6 * math.sin(a))), fill=BLUE)
        gd.point((cx, cy), fill=WHITE)
        fr.alpha_composite(g)
        out.append(fr)
    return out


def review():
    out = []
    for i in range(6):
        fr = new()
        place(fr, orca(eye="open", look=[0, 1, 1, 0, 0, 0][i], fin="up", mouth="open" if i >= 4 else "smile"), -3, 1)
        lay = new(); d = ImageDraw.Draw(lay)
        cx = [37, 39, 39, 37, 36, 36][i]; cy = 26
        d.line((cx + 3, cy + 4, cx + 8, cy + 10), fill=(90, 60, 30, 255), width=2)
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(170, 225, 255, 120), outline=BLUE, width=2)
        d.point((cx - 2, cy - 2), fill=WHITE); d.point((cx - 1, cy - 3), fill=WHITE)
        fr.alpha_composite(outline(lay))
        if i >= 4:
            d2 = bubble(fr, (34, 1, 46, 11))
            d2.line([(37, 6), (39, 8), (43, 3)], fill=GREEN, width=2)
        out.append(fr)
    return out


ROW_FNS = [
    ("idle", idle), ("running-right", swim), ("running-left", lambda: [f.transpose(Image.FLIP_LEFT_RIGHT) for f in swim()]),
    ("waving", wave), ("jumping", jump), ("failed", failed), ("waiting", waiting), ("running", working), ("review", review),
]


def main(out_dir):
    sheet = Image.new("RGBA", (COLS * W * S, ROWS * H * S), CLEAR)
    rows = {}
    for r, (name, fn) in enumerate(ROW_FNS):
        frames = fn()
        rows[name] = [f.resize((W * S, H * S), Image.NEAREST) for f in frames]
        for c, f in enumerate(rows[name]):
            sheet.paste(f, (c * W * S, r * H * S))
    os.makedirs(out_dir, exist_ok=True)
    sheet.save(os.path.join(out_dir, "spritesheet.webp"), lossless=True, quality=100)
    with open(os.path.join(out_dir, "pet.json"), "w") as fh:
        json.dump({"id": "pikorca", "displayName": "Pikorca",
                   "description": "Orca SRE de guardia: auriculares azul Freepik, lupa Magnific para las reviews y helm de k8s cuando los agentes curran."}, fh, indent=2, ensure_ascii=False)
    return rows, sheet


if __name__ == "__main__":
    rows, sheet = main(sys.argv[1])
    prev = Image.new("RGBA", sheet.size, (60, 64, 72, 255)); prev.alpha_composite(sheet)
    prev.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.NEAREST).save(sys.argv[2])
