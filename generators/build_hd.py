"""Monta una mascota HD (.codex-pet) a partir de sus poses ilustradas.

Uso: python generators/build_hd.py generators/hd/<mascota> pets/<mascota>.codex-pet [preview.png]

La carpeta de la mascota contiene meta.json (id, displayName, description y opciones)
y poses/{idle,working,review,wave,failed,waiting,jump,walk}.png sobre fondo blanco liso.
"""
import json, math, os, sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter, ImageChops

FW, FH = 256, 320          # tamaño de frame por defecto (como los sidekicks de Orca)
COLS, ROWS = 8, 9
PX = 4                     # tamaño de "pixel" de los efectos superpuestos
POSE_NAMES = ["idle", "working", "review", "wave", "failed", "waiting", "jump", "walk"]
CFG = {}
POSES = {}


def cutout(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q = deque()
    def white(c, t=232):
        return c[0] > t and c[1] > t and c[2] > t
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not white(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                q.append((nx, ny))
    # quitar halo claro pegado al borde transparente
    for _ in range(3):
        a = im.getchannel("A")
        edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(3)), a).filter(ImageFilter.MaxFilter(3))
        ep = edge.load()
        for y in range(h):
            for x in range(w):
                c = px[x, y]
                if c[3] and ep[x, y] and white(c, 190):
                    px[x, y] = (0, 0, 0, 0)
    return im.crop(im.getbbox())


def load(pet_dir):
    global FW, FH, GW, GH
    CFG.update(json.load(open(os.path.join(pet_dir, "meta.json"))))
    FW, FH = CFG.get("frame", [FW, FH])
    GW, GH = FW // PX, FH // PX
    poses = {n: cutout(os.path.join(pet_dir, "poses", n + ".png")) for n in POSE_NAMES}
    # escala común: que el más alto quepa con margen arriba para los efectos
    scale = (FH - 44) / max(p.height for p in poses.values())
    poses = {k: v.resize((round(v.width * scale), round(v.height * scale)), Image.LANCZOS) for k, v in poses.items()}
    POSES.update({k: v if v.width <= FW - 8 else v.resize((FW - 8, round(v.height * (FW - 8) / v.width)), Image.LANCZOS)
                  for k, v in poses.items()})


def frame():
    return Image.new("RGBA", (FW, FH), (0, 0, 0, 0))


def put(fr, pose, dx=0, dy=0, sx=1.0, sy=1.0, rot=0, tint=None):
    p = pose
    if sx != 1 or sy != 1:
        p = p.resize((round(p.width * sx), round(p.height * sy)), Image.LANCZOS)
    if rot:
        p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if tint:
        over = Image.new("RGBA", p.size, tint)
        p = Image.composite(Image.blend(p, over, 0.4), p, p.getchannel("A"))
    x = (FW - p.width) // 2 + dx
    y = FH - 6 - p.height + dy
    fr.alpha_composite(p, (x, y)) if x >= 0 and y >= 0 else fr.paste(p, (x, y), p)


class Pix:
    """Capa de efectos en pixel art (rejilla PX), con contorno."""
    def __init__(self):
        self.L = Image.new("RGBA", (FW // PX, FH // PX), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.L)

    def apply(self, fr, outline=True):
        L = self.L
        if outline:
            a = L.getchannel("A").point(lambda v: 255 if v else 0)
            ring = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(3)), a)
            base = Image.new("RGBA", L.size, (0, 0, 0, 0))
            base.paste(Image.new("RGBA", L.size, (14, 12, 16, 255)), mask=ring)
            base.alpha_composite(L); L = base
        fr.alpha_composite(L.resize((FW, FH), Image.NEAREST))


WHITE = (255, 255, 255, 255); GREEN = (60, 230, 120, 255); BLUE = (18, 115, 235, 255)
PINK = (255, 110, 150, 255); RED = (235, 55, 45, 255); YELLOW = (255, 210, 60, 255)
GREY = (190, 194, 204, 255); STEAM = (235, 235, 240, 200); IDLE_GREY = (205, 210, 222, 255)
GW, GH = FW // PX, FH // PX   # 64 x 80


def bubble(p, x0, y0, x1, y1):
    p.d.rounded_rectangle((x0, y0, x1, y1), 3, fill=WHITE)
    p.d.polygon([(x0 + 2, y1), (x0 + 6, y1), (x0, y1 + 4)], fill=WHITE)


def star(p, x, y, c=YELLOW):
    for q in ((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        p.d.point(q, fill=c)


def heart(p, x, y):
    p.d.polygon([(x, y + 1), (x + 2, y - 1), (x + 4, y + 1), (x + 6, y - 1), (x + 8, y + 1), (x + 4, y + 6)], fill=PINK)


# ---------------- animaciones ----------------
def idle():
    out = []
    for i in range(6):
        fr = frame()
        breathe = [0, 1, 0, 0, 1, 0][i]
        put(fr, POSES["idle"], dy=-breathe * 2, sy=1 + breathe * 0.012)
        p = Pix()
        steam = CFG.get("steam")  # [x, y] en la rejilla de efectos, p.ej. sobre una taza
        if steam and i in (1, 3, 4):
            for k in range(3):
                y = steam[1] - k * 3 - (i % 2)
                p.d.point((steam[0] + ((k + i) % 2), y), fill=STEAM)
        p.apply(fr, outline=False)
        out.append(fr)
    return out


def walk():
    out = []
    for i in range(8):
        fr = frame()
        ph = math.sin(i / 8 * 2 * math.pi)
        put(fr, POSES["walk"], dy=-round(abs(ph) * 6), rot=ph * 2.5)
        p = Pix()
        off = i % 4
        for y, ln in ((40, 4), (52, 6), (66, 3)):
            p.d.line((max(0, 8 - off - ln), y, 8 - off, y), fill=(130, 190, 255, 255))
        p.apply(fr, outline=False)
        out.append(fr)
    return out


def wave():
    out = []
    for i in range(4):
        fr = frame()
        put(fr, POSES["wave"], rot=[0, -2, 0, 2][i], dy=-[0, 2, 0, 2][i])
        p = Pix(); heart(p, 46, 8 - i * 2); p.apply(fr)
        out.append(fr)
    return out


def jump():
    out = []
    spec = [("idle", 0, 1.06, 0.9), ("jump", -24, 1, 1), ("jump", -44, 1, 1), ("jump", -24, 1, 1), ("idle", 0, 1.03, 0.96)]
    for i, (pose, dy, sx, sy) in enumerate(spec):
        fr = frame()
        tilt = CFG.get("jump_tilt", 0) * (1 if i == 2 else 0.5) if pose == "jump" else 0  # p.ej. caballito
        put(fr, POSES[pose], dy=dy, sx=sx, sy=sy, rot=tilt)
        p = Pix()
        if i == 2:
            for x, y in ((8, 16), (56, 22), (52, 6), (12, 4)):
                star(p, x, y)
        p.apply(fr, outline=False)
        out.append(fr)
    return out


def failed():
    out = []
    for i in range(8):
        fr = frame()
        dx = [0, 4, -4, 4, -4, 2, -2, 0][i]
        put(fr, POSES["failed"], dx=dx, tint=RED if i % 2 == 0 else None)
        p = Pix()
        if i % 2 == 0:
            p.d.rectangle((54, 4, 57, 13), fill=RED); p.d.rectangle((54, 15, 57, 18), fill=RED)
        for k in range(2):
            sy = 14 - ((i + k * 4) % 8) * 2
            p.d.ellipse((6 + k * 5, sy, 10 + k * 5, sy + 4), fill=GREY)
        p.apply(fr)
        out.append(fr)
    return out


def waiting():
    out = []
    for i in range(6):
        fr = frame()
        put(fr, POSES["waiting"], dx=-10, dy=-(i % 2) * 2)
        p = Pix()
        bubble(p, 44, 2, 61, 12)
        for k in range(3):
            p.d.rectangle((47 + k * 5, 6, 48 + k * 5, 7), fill=BLUE if k < i % 4 else IDLE_GREY)
        p.apply(fr)
        out.append(fr)
    return out


def working():
    out = []
    for i in range(6):
        fr = frame()
        put(fr, POSES["working"], dy=-(i % 2))
        p = Pix()
        for k in range(5):
            y = 22 - ((i * 3 + k * 5) % 22)
            x = [4, 10, 52, 58, 46][k]
            if (k + i) % 2:
                p.d.line((x, y, x, y + 4), fill=GREEN)
            else:
                p.d.rectangle((x - 1, y, x + 1, y + 4), outline=GREEN)
        p.apply(fr, outline=False)
        out.append(fr)
    return out


def review():
    out = []
    for i in range(6):
        fr = frame()
        put(fr, POSES["review"], dx=[0, -3, -5, -3, 0, 0][i], rot=[0, 1, 2, 1, 0, 0][i])
        if i >= 4:
            p = Pix(); bubble(p, 46, 1, 61, 13)
            p.d.line([(49, 7), (52, 10), (58, 4)], fill=(30, 180, 90, 255), width=2)
            p.apply(fr)
        out.append(fr)
    return out


ROWS_DEF = [
    ("idle", idle, [1680, 660, 660, 840, 840, 1920]),
    ("running-right", walk, [140] * 8),
    ("running-left", lambda: [f.transpose(Image.FLIP_LEFT_RIGHT) for f in walk()], [140] * 8),
    ("waving", wave, [220] * 4),
    ("jumping", jump, [120, 160, 220, 160, 200]),
    ("failed", failed, [140] * 8),
    ("waiting", waiting, [420] * 6),
    ("running", working, [200] * 6),
    ("review", review, [260, 260, 260, 260, 700, 900]),
]


def main(pet_dir, out_dir, preview=None):
    load(pet_dir)
    sheet = Image.new("RGBA", (COLS * FW, ROWS * FH), (0, 0, 0, 0))
    anims = {}
    for r, (name, fn, durs) in enumerate(ROWS_DEF):
        frames = fn()
        assert len(frames) == len(durs), name
        for c, f in enumerate(frames):
            sheet.paste(f, (c * FW, r * FH))
        anims[name] = {"row": r, "frames": len(frames), "frameDurationsMs": durs}
    os.makedirs(out_dir, exist_ok=True)
    sheet.save(os.path.join(out_dir, "spritesheet.webp"), lossless=True, quality=100, method=6)
    meta = {"id": CFG["id"], "displayName": CFG["displayName"], "description": CFG["description"],
            "spritesheetPath": "spritesheet.webp", "frame": {"width": FW, "height": FH}, "fps": 8,
            "defaultAnimation": "idle", "animations": anims}
    with open(os.path.join(out_dir, "pet.json"), "w") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    if preview:
        prev = Image.new("RGBA", sheet.size, (40, 44, 52, 255)); prev.alpha_composite(sheet)
        prev.convert("RGB").resize((sheet.width // 3, sheet.height // 3), Image.LANCZOS).save(preview)
    print(sheet.size, os.path.getsize(os.path.join(out_dir, "spritesheet.webp")) // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
