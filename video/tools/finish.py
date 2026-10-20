"""The teaser's finish: the 90s look over the rendered frames, the four words, and the encode.

  work/venv/bin/python tools/finish.py                    every frame to work/final/, then the encodes in out/
  work/venv/bin/python tools/finish.py --frames 96-140    just those (a range, or a list: 14,77,239)
  work/venv/bin/python tools/finish.py --no-encode        frames only
  work/venv/bin/python tools/finish.py --encode-only      the encode from work/final/ as it is

It reads work/frames/NNNN.png (tools/render: 1280 x 720, 16-bit, AgX already applied) and writes
work/final/NNNN.png at 1920 x 1080. Nothing here is random from run to run: every frame's grain,
dust, weave and flicker come from generators seeded by the frame number, so a re-run of one frame
matches the frames around it.

The look is a 16 mm print, pushed: crushed blacks, warm highlights and teal shadows, halation round
anything hot, heavy grain, a weaving gate and a flickering lamp, dust, the odd scratch, a light leak
at three cuts and one frame slip. Every stomp jolts the frame. The two shots of the laptop are a Hi8
camcorder pointed at a screen, the strobe is step-printed (each frame held for two), and every other
cut in the last run is black and white. The only words are the four in timeline.py, set in a
typewriter face. tools/flashcheck.py checks the result for flashing before anything is published.
"""
import argparse
import math
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(VIDEO, "scene"))
import timeline as TL  # noqa: E402

WORK = os.path.join(VIDEO, "work")
FRAMES = os.path.join(WORK, "frames")
FINAL = os.path.join(WORK, "final")
OUT = os.path.join(VIDEO, "out")
W, H = 1920, 1080

# The words' face: a typewriter, inked heavy and photocopied to death, as on a 90s sleeve or zine.
FONT = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"

# Per shot, in stops (the last run of cuts takes its shots' values): what the grade lifts or sinks.
TRIM = {
    "bulb": -0.1, "floor": 0.35, "wake": 0.0, "laptop": 0.25, "monitor": 0.1, "stomp": 0.25,
    "low": 0.2, "rear": 0.5, "end": 0.0, "row": 0.3,
}
HI8 = {"laptop", "monitor"}
STEP_PRINTED = {"strobe"}
# Cuts that burn in at the start: (frame, frames long, from the "left" or "right").
LEAKS = [(360, 7, "right"), (504, 5, "left"), (672, 9, "right")]
# The frame slips in the gate for two frames, showing the frame line, at the start of the last run.
SLIPS = {612: 0.28, 613: 0.12}
# Every stomp jolts the picture, as if the floor took it: down, back past, settled (pixels at 1080).
JOLTS = {}
for _f in [f for f, _ in TL.PRESSES] + [f for f, _ in TL.OLD_PRESSES]:
    for _df, _dy in ((0, 7.0), (1, -3.0), (2, 1.0)):
        JOLTS[_f + _df] = JOLTS.get(_f + _df, 0.0) + _dy
# In the last run of cuts, every other one is black and white.
MONO = {"c_flick1", "c_inside", "c_stomp", "c_press2"}
# Where each word sits, as fractions of the frame (its left edge, its baseline), its size as a
# fraction of the frame's height, and a tilt in degrees.
WORDS = {
    "fast": dict(x=0.5, y=0.88, size=0.24, tilt=-2.0),
    "seamless": dict(x=0.06, y=0.30, size=0.17, tilt=1.2),
    "open": dict(x=0.5, y=0.30, size=0.24, tilt=-1.5),
    "loud": dict(x=0.22, y=0.42, size=0.36, tilt=2.5),
}


# ---- colour ---------------------------------------------------------------------------------------

def to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def to_srgb(x):
    x = np.clip(x, 0.0, None)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def luma(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def smooth_noise(seed, t, freq):
    r = np.random.default_rng(seed)
    ph = r.random(4) * 6.283
    return float(sum(math.sin(6.283 * freq * (k + 1) * 0.73 * t + ph[k]) / (k + 1) for k in range(4)) / 2.08)


# ---- the frame ------------------------------------------------------------------------------------

def source_frame(f):
    """Which rendered frame shows at f: the strobe is step-printed."""
    shot = TL.shot_at(f)
    if shot in STEP_PRINTED:
        a = next(a for n, a, b in TL.SHOTS if n == shot)
        return a + ((f - a) // 2) * 2
    return f


def load(f):
    path = os.path.join(FRAMES, f"{f:04d}.png")
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        return np.zeros((H, W, 3), np.float32)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / (65535.0 if im.dtype == np.uint16 else 255.0)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
    return np.clip(im, 0, 1)


def weave(im, f):
    """The gate: a slow drift, a little jitter, the frame line when it slips."""
    dx = 1.6 * smooth_noise(11, f / TL.FPS, 0.35) + 0.5 * smooth_noise(12, f / TL.FPS, 3.1)
    dy = 1.2 * smooth_noise(13, f / TL.FPS, 0.3) + 0.4 * smooth_noise(14, f / TL.FPS, 2.7)
    dy += JOLTS.get(f, 0.0) * H / 1080
    if f in SLIPS:
        dy += SLIPS[f] * H
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    out = cv2.warpAffine(im, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    if f in SLIPS:
        # The next frame's tail above the line, and the line itself, black.
        line = int(SLIPS[f] * H)
        out[:line] = cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, dy - H - 0.06 * H]]), (W, H),
                                    borderMode=cv2.BORDER_REFLECT101)[:line]
        out[max(0, line - int(0.06 * H)):line] = 0.0
    return out


def halation(lin):
    """Light that went through the emulsion and back off the base: a red fringe round anything hot,
    and a wider, softer bloom."""
    hot = np.clip(lin - 0.55, 0, None)
    near = cv2.GaussianBlur(hot, (0, 0), 9)
    far = cv2.GaussianBlur(hot, (0, 0), 55)
    return near * np.float32([1.0, 0.32, 0.12]) * 1.1 + far * np.float32([1.0, 0.55, 0.3]) * 0.45


def grade(x, shot):
    """Display-space grade: crush, an S, teal shadows and warm highlights, a little less colour."""
    x = np.clip((x - 0.03) / 0.97, 0, 1)
    s = 0.42
    x = x + s * (x * x * (3 - 2 * x) - x)
    y = luma(x)[..., None]
    x = x + np.float32([-0.012, 0.010, 0.020]) * (1 - y) ** 3 + np.float32([0.035, 0.012, -0.03]) * y ** 2
    y = luma(x)[..., None]
    x = y + (x - y) * 0.8
    if shot == "end":
        x = y + (x - y) * 0.65
    return np.clip(x * 0.985 + np.float32([0.008, 0.010, 0.011]), 0, 1)


def hi8(x, f):
    """A camcorder pointed at the laptop in the dark: its automatic gain has wound the picture up, so
    it is bright and noisy; soft, the colour smeared sideways and late, ringing on edges, a tracking
    line wandering at the bottom."""
    rng = np.random.default_rng(5000 + f)
    x = np.clip(np.power(np.clip(x, 0, 1), 0.72) * 1.18, 0, 1)
    small = cv2.resize(x, (720, 405), interpolation=cv2.INTER_AREA)
    yuv = cv2.cvtColor(small, cv2.COLOR_RGB2YCrCb)
    yuv[..., 0] += cv2.GaussianBlur(rng.standard_normal((405, 720)).astype(np.float32), (0, 0), 0.6) * 0.025
    for c in (1, 2):
        noise = cv2.resize(rng.standard_normal((102, 180)).astype(np.float32), (720, 405)) * 0.012
        yuv[..., c] = np.roll(cv2.blur(yuv[..., c], (11, 1)), 4, axis=1) + noise
    yuv[..., 1:] = 0.5 + (yuv[..., 1:] - 0.5) * 1.25
    small = cv2.cvtColor(yuv, cv2.COLOR_YCrCb2RGB)
    blur = cv2.GaussianBlur(small, (0, 0), 2.2)
    small = np.clip(small + 0.7 * (small - blur), 0, 1)
    x = cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC)
    # Line jitter, worst near the bottom, and a band of noise there that crawls.
    rows = np.arange(H)
    shift = (rng.standard_normal(H) * 0.6 + np.where(rows > H * 0.93, rng.standard_normal(H) * 6, 0)).astype(np.float32)
    mapx = (np.arange(W, dtype=np.float32)[None, :] + shift[:, None])
    mapy = np.repeat(rows.astype(np.float32)[:, None], W, axis=1)
    x = cv2.remap(x, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    band = int(H * (0.95 + 0.03 * math.sin(f * 0.37)))
    x[band:band + 6] = np.clip(x[band:band + 6] + rng.random((min(6, H - band), W, 1)).astype(np.float32) * 0.5, 0, 1)
    x[::2] *= 0.94
    x = 0.03 + x * 0.95
    return np.clip(x * np.float32([0.96, 1.0, 1.03]), 0, 1)


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2 * 0.85) / 1.3
    return np.clip(1 - 0.75 * r ** 2.4, 0, 1)[..., None].astype(np.float32)


VIG = None


def aberration(x):
    """The lens: red a hair outward, blue a hair inward, at the edges."""
    out = x.copy()
    for c, k in ((0, 1.0016), (2, 0.9984)):
        m = np.float32([[k, 0, (1 - k) * W / 2], [0, k, (1 - k) * H / 2]])
        out[..., c] = cv2.warpAffine(x[..., c], m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return out


def grain(x, f, amount):
    rng = np.random.default_rng(100000 + f)
    g = rng.standard_normal((H, W)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.8) * 1.7
    c = rng.standard_normal((H // 2, W // 2, 3)).astype(np.float32)
    c = cv2.resize(cv2.GaussianBlur(c, (0, 0), 0.8), (W, H)) * 0.6
    y = luma(x)[..., None]
    a = amount * (0.55 + 1.6 * y * (1 - y) + 0.25 * (1 - y))
    return np.clip(x + a * (g[..., None] + c * 0.35), 0, 1)


def flicker(f):
    """The lamp, and a thin print: a few percent either way, a deeper dip now and then."""
    r = np.random.default_rng(200000 + f)
    v = 0.03 * smooth_noise(21, f / TL.FPS, 4.0) + 0.012 * r.standard_normal()
    if r.random() < 0.04:
        v -= 0.07
    return 1.0 + v


def dust(x, f):
    """Specks and hairs on this frame, and the scratches that run for a while."""
    rng = np.random.default_rng(300000 + f)
    layer = np.zeros((H, W), np.float32)
    for _ in range(rng.poisson(3.5)):
        cx, cy = int(rng.random() * W), int(rng.random() * H)
        r = int(1 + rng.random() ** 3 * 5)
        cv2.ellipse(layer, (cx, cy), (r, max(1, int(r * (0.5 + rng.random())))), rng.random() * 180, 0, 360,
                    float(rng.choice([1.0, -1.0])) * (0.4 + 0.5 * rng.random()), -1, cv2.LINE_AA)
    if rng.random() < 0.08:
        pts = np.cumsum(rng.standard_normal((12, 2)) * 6, axis=0) + [rng.random() * W, rng.random() * H]
        cv2.polylines(layer, [pts.astype(np.int32)], False, -0.6, 1, cv2.LINE_AA)
    # Scratches: each lives for a stretch of frames, wandering a little sideways.
    for k in range(4):
        start = 90 + k * 170 + int(np.random.default_rng(400 + k).random() * 80)
        life = 10 + int(np.random.default_rng(500 + k).random() * 18)
        if start <= f < start + life:
            r2 = np.random.default_rng(600 + k)
            x0 = r2.random() * W
            xs = x0 + 3 * math.sin((f - start) * 0.9) + rng.standard_normal() * 0.7
            cv2.line(layer, (int(xs), 0), (int(xs + r2.standard_normal() * 20), H), 0.35, 1, cv2.LINE_AA)
    layer = cv2.GaussianBlur(layer, (0, 0), 0.6)[..., None]
    return np.clip(x + layer * np.where(layer > 0, 1.0, x), 0, 1)


def leak(x, f):
    for start, n, side in LEAKS:
        if start <= f < start + n:
            t = (f - start) / n
            env = math.sin(math.pi * min(1.0, t * 1.4)) ** 1.5
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            ex = W * (1.05 - 0.45 * t) if side == "right" else W * (-0.05 + 0.45 * t)
            ey = H * (0.35 + 0.3 * t)
            d = np.sqrt(((xx - ex) / (W * 0.45)) ** 2 + ((yy - ey) / (H * 0.7)) ** 2)
            glow = np.exp(-d * d * 2.2)[..., None]
            col = np.float32([1.0, 0.38, 0.08]) * glow + np.float32([1.0, 0.85, 0.45]) * glow ** 4
            x = 1 - (1 - x) * (1 - np.clip(col * env * 1.3, 0, 1))
    return x


# ---- the words ------------------------------------------------------------------------------------

_WORD_CACHE = {}


def word_layer(word):
    """The word as an alpha mask, roughed up: inked heavy, its edges eaten, a few holes, as if it had
    been through a photocopier twice."""
    if word in _WORD_CACHE:
        return _WORD_CACHE[word]
    spec = WORDS[word]
    px = int(spec["size"] * H * 1.35)
    font = ImageFont.truetype(FONT, px)
    l, t, r, b = font.getbbox(word)
    pad = px // 3
    im = Image.new("L", (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), word, font=font, fill=255)
    a = np.asarray(im, np.float32) / 255
    rng = np.random.default_rng(sum(map(ord, word)))
    h, w = a.shape
    # Ink spread and erosion: blur, add noise at two scales, threshold.
    n1 = cv2.resize(rng.random((h // 9 + 1, w // 9 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    n2 = rng.random((h, w)).astype(np.float32)
    soft = cv2.GaussianBlur(a, (0, 0), px * 0.018)
    m = soft + 0.22 * (n1 - 0.5) + 0.18 * (cv2.GaussianBlur(n2, (0, 0), 1.2) - 0.5) * 2
    m = np.clip((m - 0.43) * 9, 0, 1)
    holes = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), px * 0.01)
    m *= np.clip(1 - (holes > np.quantile(holes, 0.985)) * 0.85, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    # Tilt it.
    rot = cv2.getRotationMatrix2D((w / 2, h / 2), spec["tilt"], 1.0)
    m = cv2.warpAffine(m, rot, (w, h), flags=cv2.INTER_LINEAR)
    _WORD_CACHE[word] = (m, pad)
    return _WORD_CACHE[word]


def words(x, f):
    for word, a, b in TL.CAPTIONS:
        if not a <= f <= b:
            continue
        m, pad = word_layer(word)
        spec = WORDS[word]
        k = f - a
        rng = np.random.default_rng(700000 + f)
        # In: two frames big and bright, then settled. Out: it stutters off.
        scale = 1.12 if k == 0 else 1.04 if k == 1 else 1.0
        alpha = 1.0
        if b - f < 3:
            alpha = (0.0, 0.85, 0.4)[b - f] if b - f < 3 else 1.0
        if rng.random() < 0.06:
            alpha *= 0.55
        mm = cv2.resize(m, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale != 1 else m
        h, w = mm.shape
        x0 = int(spec["x"] * W - pad + rng.standard_normal() * 1.5)
        y0 = int(spec["y"] * H - h + pad + rng.standard_normal() * 1.5)
        # Misregistration: now and then a red ghost a few pixels off.
        layers = [(mm, np.float32([0.93, 0.91, 0.86]), alpha, 0, 0)]
        if k < 2 or rng.random() < 0.1:
            layers.insert(0, (mm, np.float32([0.9, 0.12, 0.05]), alpha * 0.7, int(rng.integers(4, 10)), int(rng.integers(-3, 4))))
        for mk, col, al, ox, oy in layers:
            xa, ya = x0 + ox, y0 + oy
            sx0, sy0 = max(0, -xa), max(0, -ya)
            dx0, dy0 = max(0, xa), max(0, ya)
            ww, hh = min(w - sx0, W - dx0), min(h - sy0, H - dy0)
            if ww <= 0 or hh <= 0:
                continue
            region = mk[sy0:sy0 + hh, sx0:sx0 + ww, None] * al
            x[dy0:dy0 + hh, dx0:dx0 + ww] = x[dy0:dy0 + hh, dx0:dx0 + ww] * (1 - region) + col * region
    return x


# ---- one frame ------------------------------------------------------------------------------------

def finish(f):
    global VIG
    if VIG is None:
        VIG = vignette()
    shot = TL.shot_at(f)
    base = shot[2:] if shot.startswith("c_") else shot
    x = load(source_frame(f))
    x = weave(x, f)
    lin = to_lin(x) * (2.0 ** TRIM.get(base, 0.0)) * flicker(f)
    lin = lin + halation(lin)
    x = to_srgb(lin)
    if base in HI8:
        x = hi8(x, f)
    x = grade(x, base)
    if shot in MONO:
        y = luma(x)[..., None]
        y = np.clip((y - 0.04) * 1.25, 0, 1)
        x = y * y * (3 - 2 * y) * 0.35 + y * 0.65
        x = x * np.float32([0.97, 1.0, 1.03])
    x = aberration(x)
    x = x * VIG
    x = leak(x, f)
    x = words(x, f)
    x = dust(x, f)
    x = grain(x, f, 0.05 if base in HI8 else 0.042)
    # Out: the end fades away under the grain.
    if f >= TL.FRAMES - 10:
        x = x * ((TL.FRAMES - 1 - f) / 9.0) ** 1.5
    x = np.clip(x, 0, 1)
    out = (x * 255 + np.random.default_rng(900000 + f).random(x.shape) - 0.5).clip(0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(FINAL, f"{f:04d}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
    return f


# ---- the encode -----------------------------------------------------------------------------------

def encode():
    """The master and the web cuts. The soundtrack is added later, so every file here is silent.

    Grain is the costliest thing to code: H.264 at a quality setting comes to about 100 MB here, so
    the two H.264 files are two-pass at a fixed rate (the 1080p one stays under the 25 MiB a
    Cloudflare static asset may be), and the encoder smooths some of the grain away. The AV1 file is
    a little smaller and keeps the grain, which the decoder puts back (film grain synthesis).

    The frames are sRGB. Every file is converted with the BT.709 matrix and tagged so (and with the
    sRGB curve), which is what a browser assumes of HD video anyway; untagged, ffmpeg would use
    BT.601 and the page would show the colours a little off."""
    os.makedirs(OUT, exist_ok=True)
    seq = ["-framerate", str(TL.FPS), "-i", os.path.join(FINAL, "%04d.png")]
    # The tags go on the frames (setparams): ffmpeg takes the frames' over the output options.
    tags = "setparams=color_primaries=bt709:color_trc=iec61966-2-1:colorspace=bt709:range=tv"

    def scale(size=None):
        return ["-vf", (f"scale={size}:flags=lanczos:" if size else "scale=")
                + f"out_color_matrix=bt709:out_range=tv,{tags}"]

    def run(*args):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *seq, *args], check=True)

    # The master to cut the soundtrack against: ProRes 422 HQ.
    name = os.path.join(OUT, "pedal-science-teaser-master.mov")
    run(*scale(), "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", name)
    print("wrote", name)
    for label, size, rate in (("1080p", None, 5), ("720p", "1280:720", 2.5)):
        name = os.path.join(OUT, f"pedal-science-teaser-{label}.mp4")
        x264 = [*scale(size), "-c:v", "libx264", "-preset", "slow", "-b:v", f"{rate}M", "-maxrate", f"{rate * 1.4}M",
                "-bufsize", f"{rate * 2}M", "-pix_fmt", "yuv420p", "-passlogfile", os.path.join(WORK, "x264")]
        run(*x264, "-pass", "1", "-f", "mp4", os.devnull)
        run(*x264, "-pass", "2", "-movflags", "+faststart", name)
        print("wrote", name)
    name = os.path.join(OUT, "pedal-science-teaser-1080p-av1.mp4")
    run(*scale(), "-c:v", "libsvtav1", "-preset", "5", "-crf", "34", "-svtav1-params",
        "film-grain=14:film-grain-denoise=1", "-pix_fmt", "yuv420p10le", "-movflags", "+faststart", name)
    print("wrote", name)
    # The poster: the two pedals side by side, from the finished frame, after the word has gone.
    poster = next(b for n, a, b in TL.SHOTS if n == "both") - 6
    Image.open(os.path.join(FINAL, f"{poster:04d}.png")).convert("RGB").save(
        os.path.join(OUT, "pedal-science-teaser-poster.jpg"), quality=88)
    print("wrote", os.path.join(OUT, "pedal-science-teaser-poster.jpg"))


def parse_frames(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames")
    ap.add_argument("--no-encode", action="store_true")
    ap.add_argument("--encode-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    args = ap.parse_args()
    os.makedirs(FINAL, exist_ok=True)
    if not args.encode_only:
        frames = parse_frames(args.frames) if args.frames else list(range(TL.FRAMES))
        with ProcessPoolExecutor(args.jobs) as pool:
            for i, f in enumerate(pool.map(finish, frames, chunksize=4)):
                if i % 48 == 0:
                    print("finished", f, flush=True)
        print("finished", len(frames), "frames to", FINAL)
    if (args.encode_only or not (args.no_encode or args.frames)):
        encode()


if __name__ == "__main__":
    main()
