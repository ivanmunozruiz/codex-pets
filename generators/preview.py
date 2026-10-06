"""Genera las vistas previas (GIF animado + hoja PNG) de un bundle .codex-pet.

Uso: python generators/preview.py pets/<nombre>.codex-pet docs/previews/<nombre>
"""
import json, os, sys
from PIL import Image

# Valores por defecto que aplica Orca cuando pet.json no declara frame/animations
DEFAULT_FRAME = {"width": 192, "height": 208}
DEFAULT_ANIMS = {
    "idle": {"row": 0, "frames": 6, "frameDurationsMs": [1680, 660, 660, 840, 840, 1920]},
    "running-right": {"row": 1, "frames": 8}, "running-left": {"row": 2, "frames": 8},
    "waving": {"row": 3, "frames": 4}, "jumping": {"row": 4, "frames": 5},
    "failed": {"row": 5, "frames": 8}, "waiting": {"row": 6, "frames": 6},
    "running": {"row": 7, "frames": 6}, "review": {"row": 8, "frames": 6},
}
BG = (40, 44, 52)
GIF_ORDER = ["idle", "running", "waiting", "review", "failed", "waving", "jumping", "running-right"]


def main(bundle, out_prefix):
    meta = json.load(open(os.path.join(bundle, "pet.json")))
    frame = meta.get("frame", DEFAULT_FRAME)
    anims = meta.get("animations", DEFAULT_ANIMS)
    fw, fh = frame["width"], frame["height"]
    sheet = Image.open(os.path.join(bundle, meta.get("spritesheetPath", "spritesheet.webp"))).convert("RGBA")

    frames, durations = [], []
    for name in GIF_ORDER:
        a = anims[name]
        durs = a.get("frameDurationsMs") or [1000 / meta.get("fps", 8)] * a["frames"]
        for _ in range(2 if name != "idle" else 1):
            for c in range(a["frames"]):
                f = Image.new("RGBA", (fw, fh), BG + (255,))
                f.alpha_composite(sheet.crop((c * fw, a["row"] * fh, (c + 1) * fw, (a["row"] + 1) * fh)))
                frames.append(f.convert("RGB"))
                durations.append(min(int(durs[c]), 900))
    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
    frames[0].save(out_prefix + ".gif", save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)

    grid = Image.new("RGBA", sheet.size, BG + (255,))
    grid.alpha_composite(sheet)
    scale = 768 / grid.width
    grid.convert("RGB").resize((768, round(grid.height * scale)), Image.LANCZOS).save(out_prefix + "-sheet.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
