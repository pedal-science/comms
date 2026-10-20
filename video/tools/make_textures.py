"""Textures the teaser's set needs that are easier painted than built from nodes: the rug.

  work/venv/bin/python tools/make_textures.py     writes work/tex/rug.png

The rug is an invented village rug, not a copy of any real one: guard stripes, a border of stepped
diamonds, a red field with a lattice of small motifs, a central medallion with corner spandrels,
the dye uneven across rows (abrash) and the pile worn pale and dirty where feet have been. It is
drawn on a grid of "knots" so its edges step like a hand-knotted rug's.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "work", "tex")

W, H = 2100, 1450          # 1 px = 1 mm
KNOT = 6                   # mm per knot

RED = np.array([0.42, 0.07, 0.05])
DEEP = np.array([0.27, 0.035, 0.03])
NAVY = np.array([0.06, 0.07, 0.15])
CREAM = np.array([0.78, 0.70, 0.54])
GOLD = np.array([0.62, 0.45, 0.17])
GREEN = np.array([0.16, 0.25, 0.17])
RUST = np.array([0.55, 0.20, 0.08])


def noise(shape, scale, seed, octaves=4):
    """Smooth value noise in [0, 1], by summing upsampled random grids."""
    rng = np.random.default_rng(seed)
    h, w = shape
    total = np.zeros(shape)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        gh, gw = max(2, int(h / scale * 2 ** o)), max(2, int(w / scale * 2 ** o))
        g = rng.random((gh, gw))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        total += amp * np.asarray(img, dtype=np.float64) / 255.0
        norm += amp
        amp *= 0.5
    return total / norm


def main():
    os.makedirs(OUT, exist_ok=True)
    kh, kw = H // KNOT, W // KNOT
    y, x = np.mgrid[0:kh, 0:kw].astype(np.float64)
    img = np.zeros((kh, kw, 3))
    img[:] = RED

    # Distance from the edge, in knots.
    d = np.minimum.reduce([x, kw - 1 - x, y, kh - 1 - y])
    guard1 = d < 5
    border = (d >= 9) & (d < 34)
    guard2 = ((d >= 5) & (d < 9)) | ((d >= 34) & (d < 38))
    field = d >= 38

    img[guard1] = NAVY
    img[guard2] = CREAM
    # Small reciprocal stripes in the inner guard.
    stripe = guard2 & (((x + y) // 2) % 2 == 0)
    img[stripe] = RUST

    # The border: stepped diamonds along its length, on navy.
    img[border] = NAVY
    along = np.where((y < 34) | (y > kh - 35), x, y)        # the coordinate that runs along the side
    across = d - 21.5                                        # centre of the border band
    period = 26
    ph = (along % period) - period / 2
    diamond = (np.abs(ph) + np.abs(across) * 1.05) < 11
    inner = (np.abs(ph) + np.abs(across) * 1.05) < 6
    img[border & diamond] = RED
    img[border & inner] = GOLD
    dots = border & ~diamond & ((np.abs(ph) - period / 2 + 2) ** 2 + across ** 2 < 6)
    img[dots] = CREAM

    # The field: a lattice of small hooked lozenges.
    fx, fy = x - kw / 2, y - kh / 2
    lat = ((np.abs(((fx + fy) % 18) - 9) + np.abs(((fx - fy) % 18) - 9)) < 4.5)
    img[field & lat] = DEEP
    star = field & ((np.abs(((fx + 9) % 18) - 9) + np.abs(((fy + 9) % 18) - 9)) < 2.2)
    img[star] = GOLD

    # The medallion: a stepped lozenge, navy, outlined in cream, a red heart with a gold star.
    med = np.abs(fx) / 52 + np.abs(fy) / 38
    img[field & (med < 1.0)] = CREAM
    img[field & (med < 0.92)] = NAVY
    img[field & (med < 0.62)] = RED
    img[field & (med < 0.5)] = GREEN
    img[field & (med < 0.33)] = GOLD
    img[field & (np.abs(fx) / 11 + np.abs(fy) / 8 < 1.0)] = RED
    # Pendants above and below it.
    for s in (-1, 1):
        p = np.abs(fx) / 10 + np.abs(fy - s * 47) / 9
        img[field & (p < 1.0)] = NAVY
        img[field & (p < 0.55)] = CREAM
    # Corner spandrels: quarter medallions in the field's corners.
    fw, fh = kw / 2 - 38, kh / 2 - 38
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = np.abs(fx - sx * fw) / 40 + np.abs(fy - sy * fh) / 30
            img[field & (c < 1.0)] = NAVY
            img[field & (c < 0.86)] = CREAM
            img[field & (c < 0.78)] = NAVY
            img[field & (c < 0.5)] = RUST

    # Every knot its own: wool takes dye unevenly, a few percent either way.
    rng = np.random.default_rng(9)
    img = img * (1 + 0.14 * (rng.random((kh, kw)) - 0.5))[..., None]
    img = img * (1 + 0.05 * (rng.random((kh, kw, 3)) - 0.5))

    # Up to millimetres. Smoothly, so a knot is a tuft and not a pixel; then each knot a little
    # dome, its edges sunk into the pile.
    big = np.stack([np.asarray(Image.fromarray(img[..., c].astype(np.float32), mode="F")
                               .resize((kw * KNOT, kh * KNOT), Image.BICUBIC)) for c in range(3)], axis=2)
    big = np.pad(big, ((0, max(0, H - big.shape[0])), (0, max(0, W - big.shape[1])), (0, 0)), mode="edge")[:H, :W]
    yy, xx = np.mgrid[0:H, 0:W]
    cx = (xx % KNOT) - (KNOT - 1) / 2
    cy = (yy % KNOT) - (KNOT - 1) / 2
    dome = 1 - ((cx ** 2 + cy ** 2) / (2 * (KNOT / 2) ** 2))
    big = big * (0.84 + 0.16 * dome)[..., None]
    rows = noise((H, 1), 90, 3, octaves=3)
    abrash = 0.85 + 0.25 * rows
    big = big * abrash[..., None] if abrash.ndim == 2 else big * abrash
    wear = noise((H, W), 520, 7, octaves=5)
    worn = np.clip((wear - 0.48) * 3.2, 0, 1) ** 1.5
    dust = np.array([0.17, 0.14, 0.11])
    big = big * (1 - 0.45 * worn[..., None]) + dust * (0.45 * worn[..., None])
    dirt = noise((H, W), 160, 11, octaves=5)
    big *= (0.62 + 0.45 * dirt)[..., None]
    big = big * 0.85 + big.mean(axis=2, keepdims=True) * 0.15    # a little faded
    pile = np.random.default_rng(5).random((H, W))
    big *= (0.86 + 0.18 * pile)[..., None]
    big = np.clip(big, 0, 1)
    srgb = np.where(big <= 0.0031308, big * 12.92, 1.055 * np.power(big, 1 / 2.4) - 0.055)
    Image.fromarray((srgb * 255).astype(np.uint8)).save(os.path.join(OUT, "rug.png"))
    # The pile's height, for the bump: the knot domes, worn down where the rug is worn.
    height = np.clip(0.5 + 0.45 * dome - 0.3 * worn + 0.08 * (pile - 0.5), 0, 1)
    Image.fromarray((height * 255).astype(np.uint8), mode="L").save(os.path.join(OUT, "rug_height.png"))
    print("wrote", os.path.join(OUT, "rug.png"), "and rug_height.png")


if __name__ == "__main__":
    main()
