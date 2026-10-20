"""Count flashes in the finished frames against WCAG 2.3.1's general-flash rule, before anything is
published.

  work/venv/bin/python tools/flashcheck.py [work/final]

A transition is a change of relative luminance of at least 0.1 between consecutive frames, where the
darker of the two is below 0.8, over at least a quarter of the frame (the rule's limit is a quarter
of any 10-degree field of view, which on a laptop at arm's length is most of a small video: a
quarter of the frame is the stricter reading for a page that plays it full width). A flash is a pair
of opposing transitions. The rule allows three flashes in any one second; this exits non-zero on more,
and prints the worst second either way.
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scene"))
import timeline as TL  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "work", "final")


def rel_luminance(path):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    im = cv2.resize(im, (192, 108), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)
    return lin[..., 2] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 0] * 0.0722


frames = sorted(int(f[:4]) for f in os.listdir(src) if f.endswith(".png") and f[:4].isdigit())
prev, trans = None, {}
for f in frames:
    lum = rel_luminance(os.path.join(src, f"{f:04d}.png"))
    if prev is not None:
        d = lum - prev
        darker = np.minimum(lum, prev)
        up = ((d >= 0.1) & (darker < 0.8)).mean()
        down = ((d <= -0.1) & (darker < 0.8)).mean()
        if up >= 0.25:
            trans[f] = +1
        elif down >= 0.25:
            trans[f] = -1
    prev = lum

# A flash completes when a transition opposes the last one.
flashes, last = [], 0
for f in sorted(trans):
    if last and trans[f] == -last:
        flashes.append(f)
        last = 0
    else:
        last = trans[f]

worst, at = 0, None
for f in frames:
    n = sum(1 for x in flashes if f <= x < f + TL.FPS)
    if n > worst:
        worst, at = n, f
print(f"{len(trans)} transitions, {len(flashes)} flashes; the worst second has {worst}"
      + (f", from frame {at} ({TL.shot_at(at)})" if at is not None else ""))
print("flashes at frames:", flashes)
sys.exit(1 if worst > 3 else 0)
