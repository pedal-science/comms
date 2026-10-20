# The teaser

Thirty seconds of the pedal in a dark room, shot like a 90s grunge video: a bare bulb on its flex, a
rug, a streetlight through half-shut blinds, the pedal waking, stomps, a strobe. No people and no
narration; the only words on screen are **fast**, **seamless**, **open** and **loud**. It is silent:
the soundtrack, the owner playing the pedal, goes on afterwards (below). It is separate from the long video in
[outline.md](outline.md), and can be the website's hero loop until that exists.

Everything in it is rendered: the 3D models from `pedal.project/enclosure/`, a set built in code
around them, and the two screens showing **real screenshots** of rigpa and ljoss, captured from one
engine running one rig. The footswitch presses are simulated — the caps move, the screen changes —
because the footswitches are not working yet; the stomp shoot in the outline waits for them.

| | Frames | What it shows |
|---|---|---|
| Pickup | 0–35 | The bulb flickers on and swings |
| | 36–83 | The pedal; its screen boots |
| **fast** | 84–227 | The rig on the bar screen, blocks toggled on the beat; one bar of a footswitch |
| **seamless** | 228–419 | Echo off and a third amp on the pedal's touch screen; the same rig on a laptop in ljoss, where the IR goes off; back on the pedal, which shows it, the echo comes on; in ljoss again, the IR comes back |
| **open** | 420–563 | Both enclosures side by side — the console (current) and the 1590DD box (the other build) — the old one's press, the console with its lid off |
| **loud** | 564–659 | A stomp, then the strobe on every beat with the IR switched in and out |
| Out | 660–719 | The pedals from above while the bulb dies; the last three beats fade to black |

The rig is the owner's: the Boss SD-1 (APP-SD1-Drive-II) into the Orange Rockerverb (ORNG-V30-e609),
in parallel with the Ampeg VT-40, then the Deftones *Diamond Eyes* IR and a tape echo; the third
lane added on screen is RIFF TAPE's Green Russian + OR120 + PPC412. ljoss carries NAM captures only
in amp blocks, so the SD-1 sits in one there (rigpa names it by its capture). rigpa shows each
capture by the name stored in it, which for the Green Russian is its trainer's.

## The grid, for the soundtrack

**24 fps, 720 frames, 4/4 at 120 BPM**: a beat is 12 frames (0.5 s), a bar 48 (2 s), and the video
starts on **beat 2** of a bar. So the first three beats are a pickup, the downbeats fall on frames
36, 84, 132 … 708 (0:01.5, 0:03.5, 0:05.5 … 0:29.5), and the music's last three beats, from 0:28.5,
are its fade, which the picture follows to black. Every cut and every word starts on a downbeat;
presses, screen toggles and strobe hits fall on beats.

| At | Frame | |
|---|---|---|
| 0:03.5 | 84 | **fast** |
| 0:09.5 | 228 | **seamless** |
| 0:17.5 | 420 | **open** |
| 0:23.5 | 564 | **loud**; the strobe fires on every beat from 0:25.5 to 0:27.0 |
| 0:27.5 | 660 | out; the bulb dies from 0:28.0, black at 0:30 |

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
