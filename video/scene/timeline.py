"""The teaser's edit, in frames: one place for the shots, the presses, what each screen shows and
the captions. The scene build (build_scene.py), the screen plates (make_plates.py) and the finish
(finish.py) all read it, so a cut moved here moves everywhere.

24 fps, 30 s, 720 frames. Cuts sit on a 120 BPM grid — a beat is 12 frames, a bar 48 — so a
soundtrack at 120 (or 60, or 240) BPM drops onto it with the cuts on the beat.
"""

FPS = 24
FRAMES = 720
BEAT = 12
BAR = 4 * BEAT

# (name, first frame, last frame). Each shot has its own camera, CAM_<name>.
SHOTS = [
    # Cold open: the room before the pedal.
    ("bulb", 0, 29),
    ("floor", 30, 59),
    ("wake", 60, 95),
    # fast
    ("press1", 96, 107),
    ("flick1", 108, 119),
    ("press2", 120, 131),
    ("flick2", 132, 143),
    ("whip", 144, 167),
    ("row", 168, 191),
    ("rack", 192, 215),
    # seamless
    ("touch", 216, 263),
    ("laptop", 264, 299),
    ("bar", 300, 329),
    ("monitor", 330, 359),
    # open
    ("both", 360, 407),
    ("old", 408, 431),
    ("inside", 432, 461),
    ("rear", 462, 503),
    # loud
    ("stomp", 504, 527),
    ("strobe", 528, 575),
    ("low", 576, 611),
    # the last run of cuts, six frames each, borrows the cameras above
    ("c_press1", 612, 617), ("c_flick1", 618, 623), ("c_old", 624, 629), ("c_inside", 630, 635),
    ("c_row", 636, 641), ("c_monitor", 642, 647), ("c_stomp", 648, 653), ("c_rear", 654, 659),
    ("c_press2", 660, 665), ("c_flick2", 666, 671),
    # out
    ("end", 672, 719),
]


def shot_at(frame):
    for name, a, b in SHOTS:
        if a <= frame <= b:
            return name
    return None


def camera_for(name):
    """The run of cuts at the end reuses the cameras of the shots it names."""
    return "CAM_" + (name[2:] if name.startswith("c_") else name)


# Footswitch presses on the console: (frame, switch). Switches 1-5 are the row, "T" the tuner.
PRESSES = [
    (99, 3), (121, 1), (126, 2), (138, 4),
    (170, 1), (174, 2), (178, 3), (182, 4), (186, 5),
    (506, 3), (528, 2), (540, 4), (552, 1), (564, 3), (588, 3), (600, 5),
    (615, 3), (651, 3), (663, 2),     # each on the switch its cut's camera is looking at
]

# Presses on the old 1590DD pedal: (frame, switch "A" "B" or "C").
OLD_PRESSES = [(416, "B"), (627, "A")]

# What the console's bar screen shows: (first frame, image). Images are relative to work/ui/.
# "off" is the panel dark, "boot" its first flicker.
BAR_SCREEN = [
    (0, "off"),
    (70, "boot"),
    (78, "rigs/Clean.png"),
    (100, "rigs/Lead.png"),
    (115, "rigs/Sludge.png"),
    (122, "rigs/Clean.png"),
    (127, "rigs/Lead.png"),
    (133, "rigs/Clean.png"),
    (137, "rigs/Lead.png"),
    (139, "rigs/Sludge.png"),
    (171, "rigs/Clean.png"),
    (175, "rigs/Lead.png"),
    (179, "rigs/Sludge.png"),
    (183, "rigs/Lead.png"),
    (187, "rigpa/00-start.png"),
    (237, "rigpa/01-echo-off.png"),
    (285, "rigpa/02-third-amp.png"),
    (319, "rigpa/03-echo-on.png"),
    (507, "rigs/Lead.png"),
    (529, "rigs/Clean.png"),
    (541, "rigpa/03-echo-on.png"),
    (553, "rigs/Lead.png"),
    (565, "rigs/Sludge.png"),
    (589, "rigpa/03-echo-on.png"),
    (601, "rigs/Lead.png"),
    (616, "rigs/Clean.png"),
    (652, "rigs/Lead.png"),
    (664, "rigpa/03-echo-on.png"),
]

# Touches on the bar screen, drawn as a ring where a finger would be: (frame, x, y) in the
# screen's own 1920 x 480 pixels.
TOUCHES = [
    (233, 1268, 232),   # the delay: off
    (281, 1400, 32),    # the + (the palette): a third amp
    (315, 1268, 285),   # the delay: on again (lower: the third lane pushed it down)
]

# What ljoss shows on the laptop: (first frame, image), relative to work/ui/.
LAPTOP_SCREEN = [
    (0, "ljoss/01-echo-off.png"),
    (282, "ljoss/02-third-amp.png"),
    (322, "ljoss/03-echo-on.png"),
]

# The four words, each once: (word, first frame, last frame).
CAPTIONS = [
    ("fast", 103, 125),
    ("seamless", 222, 251),
    ("open", 366, 395),
    ("loud", 507, 533),
]

# Frames the strobe fires on, in the strobe shot: two frames on every beat, which is two flashes a
# second. Each lands with a stomp (PRESSES). Faster strobing is out: a page that plays this must stay
# under three flashes a second (WCAG 2.3.1).
STROBE = [f for f in range(528, 576) if (f - 528) % BEAT in (0, 1)]
