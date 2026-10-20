# The teaser

Thirty seconds of the pedal in a dark room, shot like a 90s grunge video: a bare bulb on its flex, a
rug, a streetlight through half-shut blinds, the pedal waking, stomps, a strobe. No people and no
narration; the only words on screen are **fast**, **seamless**, **open** and **loud**. It is silent:
the soundtrack is added afterwards (below). It is separate from the long video in
[outline.md](outline.md), and can be the website's hero loop until that exists.

Everything in it is rendered: the 3D models from `pedal.project/enclosure/`, a set built in code
around them, and the two screens showing **real screenshots** of rigpa and ljoss, captured from one
engine running one rig. The footswitch presses are simulated — the caps move, the screen changes —
because the footswitches are not working yet; the stomp shoot in the outline waits for them.

| | Frames | What it shows |
|---|---|---|
| Cold open | 0–95 | The bulb flickers on and swings. The floor. The pedal's screen boots |
| **fast** | 96–215 | Presses and the bar screen flicking between rigs; a whip pan; the row of switches; a rack focus |
| **seamless** | 216–359 | One edit made twice: on the pedal's touch screen (echo off, a third amp, echo on) and the same rig, same edits, in ljoss on a laptop |
| **open** | 360–503 | Both enclosures side by side — the console (current) and the 1590DD box (the other build) — the old one's press, the console with its lid off, the rear panel's jacks |
| **loud** | 504–611 | Stomps, a strobe on the beat, a low shot under the strip light |
| Out | 612–719 | Ten six-frame cuts, then the pedals from above while the bulb dies |

## The grid, for the soundtrack

**24 fps, 720 frames, 120 BPM**: a beat is 12 frames (0.5 s), a bar 48 (2 s). Every section starts
on a beat and every cut on a beat or a half beat, so music at 120 BPM (or 60 or 240) starting at
0:00.000 sits on the cuts.

| At | Frame | Beat |
|---|---|---|
| 0:04.0 | 96 | **fast**: the presses start |
| 0:09.0 | 216 | **seamless** |
| 0:15.0 | 360 | **open** |
| 0:21.0 | 504 | **loud**: the strobe fires on every beat from 0:22.0 to 0:23.5 |
| 0:25.5 | 612 | the last run of cuts, one every half beat |
| 0:28.0 | 672 | out; the bulb dies at 0:28.75–0:29.5, black by 0:30 |

Every press is in `scene/timeline.py` (`PRESSES`), so hits can be placed on them. To put the
soundtrack on, with the files from `out/`:

```bash
ffmpeg -i out/pedal-science-teaser-1080p.mp4 -i soundtrack.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest pedal-science-teaser.mp4
```

The strobe stays at **two flashes a second at most**, under the three a second that WCAG 2.3.1
allows for a page that plays it; a recut must keep it there.

## How it is made

`scene/timeline.py` is the edit: every shot, press, screen change, touch and word, in frames. The
scene, the screen plates and the finish all read it, so a cut moved there moves everywhere.

| Step | Tool | Makes |
|---|---|---|
| 1. The engine | `tools/dev-backend` | `namchaind` and `pedald` on this Mac (ports 47816 and 47826), laid out by rigpa's `dev/dev-pedal` in `work/dev/`, charging rigs from **vip's own cost table** |
| 2. The screens | `tools/capture-ui` | `work/ui/`: ljoss's window after each edit in `ui/demo.json`, and rigpa's 1920 × 480 screen at the same moment, plus each rig rigpa shows in the quick flicks |
| 3. Plates and textures | `tools/make_plates.py`, `tools/make_textures.py` | `work/plates/`: what each screen shows on every frame, with the touches drawn; `work/tex/`: the rug |
| 4. The scene and the render | `tools/render` | `work/video.blend` from `scene/build_scene.py`, then `work/frames/` (1280 × 720, 16-bit, about 5 s a frame on this Mac; `--scale 150` for 1080p) |
| 5. The finish | `tools/finish.py` | `work/final/` (1920 × 1080) and `out/`: the ProRes master, H.264 at 1080p (about 19 MB, under Cloudflare's 25 MiB per asset) and 720p (about 9 MB), AV1 at 1080p (about 16 MB, keeping the grain the H.264 smooths away: the decoder puts it back), and a poster. All are BT.709 and tagged as sRGB |

Steps 1 and 2 are needed only when a screen changes. `tools/contact.py` makes a contact sheet of
any of the frame folders, for looking at the cut.

**Needs:** Blender 5.2 on `PATH`; `pedal.project/enclosure/console.blend` and `pedal.blend` (the
enclosure's README says how to build or fetch them); `ffmpeg` with libx264 and libsvtav1; a Python
venv at `work/venv` with numpy, Pillow and opencv-python; macOS's Courier New Bold for the words; for
steps 1 and 2, `namchain/build-mac/namchaind`, rigpa's `build/mac-debug` and the ljoss demo build
below. `tools/flashcheck.py` checks the finished frames for flashing (WCAG 2.3.1) and fails above
three a second.

**The ljoss demo build.** ljoss's `DemoMode` (`Ljoss/App/DemoMode.swift`, macOS only) runs a script
when `LJOSS_DEMO` names a folder holding a `demo.json`: it builds the script's rig, connects to the
engine it names and makes its edits through the editor's own calls, saving the window after each.
It touches nothing of the user's — no preferences, no keychain, its own library. It is built ad hoc
signed under its own bundle id, so it never replaces the real app:

```bash
xcodebuild -project ../../ljoss/Ljoss.xcodeproj -scheme Ljoss -destination 'platform=macOS' -derivedDataPath ../../ljoss/build/dd-demo PRODUCT_BUNDLE_IDENTIFIER=cc.hemsley.ljoss.demo CODE_SIGN_IDENTITY=- CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM= build
```

**The cost table.** Without one the dev engine charges every model the unknown cost, a quarter of a
core, and refuses the video's rig — three amps in parallel — as over budget, which on the pedal it is
not. `tools/dev-backend` gives it vip's measured table plus a row for each of the four macro blocks
the rig uses that the table does not price yet (tone stack, cab, tilt EQ, feedback delay), each the
sum of the primitives it lowers to at vip's own figures. They exist so rigpa shows the rig's health
as *ok* rather than *charged the unknown cost*, and live only in `work/dev/cost-video.json`.

## What it shows, and the rules

- **Both enclosures are shown, as two builds anyone might make**: the Hammond 1456RH3 console with
  the 8.8″ bar screen (current) and the 1590DD box with the 2.4″ screen (the earlier layout). Both
  are design renders, not drilling templates (`pedal.project/enclosure/README.md`).
- The rigs are real rigs on a real engine; their models and IRs are from `~/Documents/Audio` and are
  only named on the screens, as rigpa and ljoss name them. Nothing is heard.
- No claim is made beyond the four words; [../docs/claims.md](../docs/claims.md) carries what the
  teaser rests on.
- `work/` (everything generated) and `out/` (the encodes; the master is about 700 MB) are not in git.
