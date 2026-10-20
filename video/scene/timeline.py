"""The teaser's edit, in frames: one place for the shots, the presses, what each screen shows and
the words. The scene build (build_scene.py), the screen plates (make_plates.py) and the finish
(finish.py) all read it, so a cut moved here moves everywhere.

24 fps, 30 s, 720 frames, cut to the owner's own playing: 4/4 at 120 BPM, a beat every 12 frames,
and the video starts on beat 2 of a bar. So the first three beats are a pickup, the music's
downbeats fall on frames 36, 84, 132 ... 708 (DOWNBEATS), and the last three beats, 684 on, fade out.
Every cut and every word starts on a downbeat; presses, toggles and strobe hits fall on beats.
"""

FPS = 24
FRAMES = 720
BEAT = 12
BAR = 4 * BEAT
PICKUP = 3 * BEAT                       # beats 2, 3 and 4 of the first bar
DOWNBEATS = list(range(PICKUP, FRAMES, BAR))
FADE_FROM = FRAMES - 3 * BEAT           # the music fades over its last three beats; so does the picture

# (name, first frame, last frame). Each shot has its own camera, CAM_<name>.
SHOTS = [
    # The pickup: the bulb flickers on. The first downbeat wakes the pedal.
    ("bulb", 0, 35),
    ("wake", 36, 83),
    # fast: the rig on the screen, blocks toggled on the beat; one bar of a footswitch.
    ("flick2", 84, 131),
    ("press1", 132, 179),
    ("flick1", 180, 227),
    # seamless: an edit made on the pedal's screen shows in ljoss, and one made in ljoss on the pedal.
    ("touch", 228, 275),
    ("laptop", 276, 323),
    ("bar", 324, 371),
    ("monitor", 372, 419),
    # open: both builds; the old one; the console with its lid off.
    ("both", 420, 467),
    ("old", 468, 515),
    ("inside", 516, 563),
    # loud: a stomp, then the strobe on every beat.
    ("stomp", 564, 611),
    ("strobe", 612, 659),
    # out: the pedals from above while the bulb dies, and the fade.
    ("end", 660, 719),
]


def shot_at(frame):
    for name, a, b in SHOTS:
        if a <= frame <= b:
            return name
    return None


def span(name):
    return next((a, b) for n, a, b in SHOTS if n == name)


def camera_for(name):
    return "CAM_" + name


assert all(a in DOWNBEATS for _, a, _ in SHOTS[1:]), "every cut on a downbeat"

# The screen comes on a beat into the pedal's shot: the boot flicker, then the rig.
BOOT = 48

# Footswitch presses on the console: (frame, switch). Switches 1-5 are the row, "T" the tuner.
PRESSES = [
    (144, 3), (168, 3),                 # press1, toggling the drive
    (564, 3), (588, 3),                 # the stomp
    (624, 1), (636, 2), (648, 1),       # under the strobe
]

# Presses on the old 1590DD pedal: (frame, switch "A" "B" or "C"), and when its LED answers.
OLD_PRESSES = [(480, "B")]
OLD_LED_ON = 482

# What the console's bar screen shows: (first frame, image). Images are relative to work/ui/.
# "off" is the panel dark, "boot" its first flicker. The states are the rig captured after each of
# ui/demo.json's edits, the same on both screens.
S = {k: f"rigpa/{k}.png" for k in ("01-drive-off", "02-drive-on", "03-echo-off", "04-third-amp",
                                    "05-ir-off", "06-echo-on", "07-ir-on")}
BAR_SCREEN = [
    (0, "off"),
    (BOOT, "boot"),
    (BOOT + 8, S["02-drive-on"]),
    # fast: the drive off and on, then the echo, on the beat.
    (97, S["01-drive-off"]),
    (109, S["02-drive-on"]),
    (121, S["01-drive-off"]),
    (145, S["02-drive-on"]),            # the footswitch, offscreen
    (169, S["01-drive-off"]),
    (193, S["02-drive-on"]),
    (205, S["03-echo-off"]),
    (217, S["02-drive-on"]),
    # seamless: echo off and a third amp here; the IR goes off in ljoss; the echo comes back here.
    (241, S["03-echo-off"]),
    (265, S["04-third-amp"]),
    (301, S["05-ir-off"]),
    (345, S["06-echo-on"]),
    (397, S["07-ir-on"]),               # made in ljoss
    # loud: the IR in and out under the strobe.
    (625, S["06-echo-on"]),
    (637, S["07-ir-on"]),
    (649, S["06-echo-on"]),
    (660, S["07-ir-on"]),
]

# Touches on the bar screen, drawn as a ring where a finger would be: (frame, x, y) in the
# screen's own 1920 x 480 pixels. Each lands a few frames before the change it makes.
SD1, DELAY, PLUS, DELAY_LOW = (626, 180), (1268, 233), (1400, 32), (1268, 285)
TOUCHES = [
    (93, *SD1), (105, *SD1), (117, *SD1),
    (189, *SD1), (201, *DELAY), (213, *DELAY),
    (237, *DELAY),
    (261, *PLUS),
    (341, *DELAY_LOW),                  # the third lane has pushed the row down
]

# What ljoss shows on the laptop: (first frame, image), relative to work/ui/.
LAPTOP_SCREEN = [
    (0, "ljoss/02-drive-on.png"),
    (241, "ljoss/03-echo-off.png"),
    (265, "ljoss/04-third-amp.png"),
    (301, "ljoss/05-ir-off.png"),
    (345, "ljoss/06-echo-on.png"),
    (397, "ljoss/07-ir-on.png"),
]

# The four words, each once, each landing on a downbeat: (word, first frame, last frame).
CAPTIONS = [
    ("fast", 84, 113),
    ("seamless", 228, 257),
    ("open", 420, 449),
    ("loud", 564, 593),
]

# Frames the strobe fires on: two frames on every beat of its shot, which is two flashes a second.
# Faster strobing is out: a page that plays this must stay under three flashes a second (WCAG 2.3.1).
STROBE = [f for f in range(*span("strobe")) if (f - span("strobe")[0]) % BEAT in (0, 1)]
