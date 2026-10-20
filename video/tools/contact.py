"""A contact sheet of rendered stills, labelled with frame and shot, for reviewing the cut.

  work/venv/bin/python tools/contact.py <dir> <out.png> [frames,...]
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scene"))
import timeline as TL  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
frames = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else sorted(
    int(f[:4]) for f in os.listdir(src) if f.endswith(".png") and f[:4].isdigit())
tw, th, cols = 400, 225, 4
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(frames):
    p = os.path.join(src, f"{f:04d}.png")
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGB").resize((tw, th))
    x, y = (i % cols) * tw, (i // cols) * (th + 18)
    sheet.paste(im, (x, y + 18))
    d.text((x + 4, y + 3), f"{f}  {TL.shot_at(f)}", fill=(255, 255, 0))
sheet.save(out)
print(out, sheet.size)
