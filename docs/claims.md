# Claims and their evidence

Every claim the website or the video makes, its public wording, and where it comes from. Paths are
relative to the workspace root (`~/code.local/pedal/`), so `pedal.project/…` is that repository.
Compiled 2026-10-19 and revised the same day with the owner's decisions. **Re-read a source before
quoting a number from it**: the evidence moves on and this file does not move with it by itself.

The owner's position (2026-10-19): this is not a product and nothing is sold, so publishing does
not wait on re-measurement or comparisons. Latency figures and rig sizes are not quoted; the NAM
figures are, and they are the Raspberry Pi 5's.

Columns: **Public wording** is what the site and video say. **Behind it** is the evidence and any
internal note — the notes are for us, not for the page.

## 1. NAM and IR: more per rig

| ID | Public wording | Behind it |
|---|---|---|
| C1 | NAM's A2 Full runs **2× faster** on the Raspberry Pi 5's processor | 2.14× at 64-frame blocks (2.00–2.35× over 32–256). Measured on a Raspberry Pi 500 — the same BCM2712, 4× Cortex-A76 at 2.4 GHz as the Pi 5. `namchain/plan.md` §11 (the PR #313 A/B), `namchain/bench-results/pr313-planar-ab.csv`; upstream as NeuralAmpModelerCore PR #313 |
| C2 | …and A2 Lite **3× faster** | 3.01× at 64 (2.96–3.14×). As C1 |
| C3 | **8 full-quality NAM models in use all at once on a Pi 5** | The owner's deliberately conservative figure (2026-10-20: 9 "a bit too overblown"). Measured on one core of vip (Pi 5, 1 GB): 9 A2 Full fit with p99 at 97.4 % of the 1.33 ms deadline, 8 at 82.2 %; 30 A2 Lite (0.111 and 0.0333 of a core). `pedal.project/bench-results/2026-10-08-cost-table-vip/README.md`, `pedal.project/devices/vip/rootfs/etc/namchain/cost.json`. The 8 all fit on one core; never multiply by the three audio cores |
| C4 | Long IRs cost a fraction of what they did | At 8192 taps and 64 frames on the Pi 500, p99 8.70 % → 1.97 % of the deadline (`linear` → `linearplus`); 52–57 % lower mean from 2048 taps. `NAMBench/BENCHMARKING.md` "Impulse responses", `NAMBench/IR-PATH.md`. Proposed to NeuralAmpModelerCore as `linearplus`. Internal: check which convolver namchain ships before saying the pedal uses it |
| C5 | The optimisations are public, contributed to NAM | PR #313 (NEON), `linearplus` (IR). Link both from the site |

Not used publicly: the M2 and M1 figures (NAMBench's `PRESENTATION.md`, the third-party M1
reproduction). The Pi is the target.

## 2. Switching

| ID | Public wording | Behind it |
|---|---|---|
| C6 | **Extremely low latency switching, even of a fully loaded rig** | Engine handover to a warm rig: `handover_blocks: 3` + 5 ms fade, ~9 ms (`pedal.project/docs/managing-processing-power-and-optimising-for-fast-switching.md`, T7). Cold: a Lite stand-in audible 41 ms after the press (T9). Not quoted. Internal note: a press through `pedald` measured 108–110 ms, ~100 ms of it its HTTP round trip (T9) — the footswitch path should lose that before the stomp scenes are shot |
| C7 | **No audible switching artefacts, no dropouts** | Mechanism: per-sample ramps, dual-render crossfades (`namchain/docs/transitions.md`). Runs: T7 and T10 (0 xruns), the 2026-10-13 heavy-rig playtest (0 glitches, `pedal.project/bench-results/2026-10-13-two-heavy-rigs-playtest.png`). Internal note: holds for a switch to a warm rig, which is what a press in a bank does; on a *cold* switch the full model crossfades in from a cold start (T9, P8 not achieved on the board), so film switches between warm rigs |

Measured and not quoted: about 3.8 ms jack to jack at 64-frame periods
(`pedal.project/docs/codec-bringup-2a.md`, 2026-09-27).

## 3. Audio quality

| ID | Public wording | Behind it |
|---|---|---|
| C8 | **Excellent audio quality**, with every measurement published | The converter and noise runs in `pedal.project/docs/codec-bringup-2a.md`, `pedal.project/bench-results/` and `pedal.project/noise-tests/`. No figure quoted in the headline |

## 4. Hardware and open designs

| ID | Public wording | Behind it |
|---|---|---|
| C9 | Built from standard parts: Raspberry Pi 5, Raspberry Pi Pico 2, a codec board, analogue boards you can solder | `pedal.project/docs/hardware-handoff.md`, `pedal.project/docs/bom.md`. The SparkFun WM8960 board is retired: the build page needs to say what replaces it |
| C10 | Schematics generated from wiring tables and checked against KiCad's netlist; board layouts as data, checked against the netlist | `pedal.project/schematic/`, `pedal.project/stripboard/` |
| C11 | The software image is built from pinned commits; a bad kernel falls back by itself | `pedal.project/docs/vip-image.md`, `rtpi/README.md` |
| C12 | The enclosure and its screen, as 3D models: the console, and the 1590DD box as the other build | **Made.** `pedal.project/enclosure/` holds both: the console model (Hammond 1456RH3 with the Prechen 8.8″ 1920×480 touch bar, D14), and the 1590DD model with the 2.4″ screen, which is shown as a build anyone might make, not as superseded (owner, 2026-10-20). Both are design renders: the console's panel positions are read off the owner's chalk (`pedal.project/imaginings/big-enclosure/panel-sketch/`) and nothing is drilled. Captioned renders say so; the teaser (`video/README.md`) carries no words but its four, so a page that plays it says so beside it |

## 5. Where it surpasses: the comparison that would substantiate it

The two claims in [message.md](message.md) are published as the owner's assessment. This is the
quantitative work that would back them, done when it is done; publishing does not wait for it.

| Claim | Ours | Compare against | What it needs |
|---|---|---|---|
| More NAM and IR per rig than any product on the market | C3, C4 | Units that run captures or NAM: e.g. Neural DSP Quad Cortex, IK Multimedia TONEX, Line 6 Helix Stadium, Fractal, Kemper, HeadRush | Each one's published limit on captures/models and IRs per preset, and whether it runs NAM at A2 quality |
| Low-latency switching at that load, without dropouts or artefacts | C6, C7 | The same units | Their published switching gap and spillover; ideally the same switch recorded on each, at the jack, with a comparable load |
| Open code and designs | C5, C9–C11 | All of them | Nothing: true by inspection |
