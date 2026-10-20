"""The screens' pictures, frame by frame: what the console's bar screen and the laptop show at each
of the teaser's 720 frames, from timeline.py and the captures in work/ui/.

  work/venv/bin/python tools/make_plates.py

writes work/plates/bar/NNNN.png (1920 x 480, the panel's own resolution) and
work/plates/laptop/NNNN.png, numbered by frame. Blender maps them onto the screens in the scene.
A touch is drawn as a ring where a finger would be, since there is no finger.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(VIDEO, "scene"))
import timeline as TL  # noqa: E402

UI = os.path.join(VIDEO, "work", "ui")
OUT = os.path.join(VIDEO, "work", "plates")
BAR = (1920, 480)
LAPTOP = (1600, 1000)

_cache = {}


def load(name, size):
    key = (name, size)
    if key not in _cache:
        im = Image.open(os.path.join(UI, name)).convert("RGB")
        if im.size != size:
            # Fit by width and crop or pad the height: the ljoss window is taller than 16:10.
            w, h = size
            scaled = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            canvas = Image.new("RGB", size, (24, 24, 26))
            canvas.paste(scaled.crop((0, 0, w, min(h, scaled.height))), (0, 0))
            im = canvas
        _cache[key] = im
    return _cache[key]


def state(table, frame):
    current = table[0][1]
    for start, name in table:
        if frame >= start:
            current = name
    return current, max(s for s, _ in table if s <= frame)


def bar_frame(f):
    name, since = state(TL.BAR_SCREEN, f)
    if name == "off":
        return Image.new("RGB", BAR, (0, 0, 0))
    if name == "boot":
        # A panel waking: dark, a white flash of the backlight, a black frame, then the UI.
        k = f - since
        level = [0.0, 0.9, 0.15, 0.6, 0.05, 1.0, 0.4, 0.8][min(k, 7)]
        nxt = state(TL.BAR_SCREEN, since + 8)[0]
        ui = load(nxt, BAR)
        arr = np.asarray(ui, dtype=np.float32) * level + 20 * level
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    im = load(name, BAR).copy()
    if f - since < 2 and since > 80:
        # A rig change: the panel redraws, so the first frame of a new picture is a touch brighter.
        im = Image.fromarray(np.clip(np.asarray(im, dtype=np.float32) * 1.25 + 8, 0, 255).astype(np.uint8))
    for t, x, y in TL.TOUCHES:
        k = f - t
        if 0 <= k < 12:
            draw_touch(im, x, y, k)
    return im


def draw_touch(im, x, y, k):
    """A finger's touch, without the finger: a soft dot that lands and a ring that spreads."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    p = k / 11
    r = 18 + 70 * p
    a = int(230 * (1 - p) ** 1.5)
    d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, a), width=8)
    r2 = 10 + 40 * p
    d.ellipse([x - r2, y - r2, x + r2, y + r2], outline=(255, 255, 255, a // 2), width=4)
    if k < 5:
        rr = 24
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, int(190 * (1 - k / 5))))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    im.paste(layer, (0, 0), layer)


def laptop_frame(f):
    name, since = state(TL.LAPTOP_SCREEN, f)
    return load(name, LAPTOP)


def main():
    for sub in ("bar", "laptop"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for f in range(TL.FRAMES):
        bar_frame(f).save(os.path.join(OUT, "bar", f"{f:04d}.png"), compress_level=1)
        laptop_frame(f).save(os.path.join(OUT, "laptop", f"{f:04d}.png"), compress_level=1)
    print("wrote", TL.FRAMES, "frames of each to", OUT)


if __name__ == "__main__":
    main()
