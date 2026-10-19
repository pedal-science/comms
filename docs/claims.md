# Claims and their evidence

Every number or claim the website or the video makes, and where it comes from. Paths are relative to
the workspace root (`~/code.local/pedal/`), so `pedal.project/…` is that repository. Compiled
2026-10-19 by reading the sources; **re-read the source before publishing**, because the evidence
moves on and this file does not move with it by itself.

Status:
- **measured** — a recorded measurement says it; safe to publish as worded.
- **qualified** — measured, but only with the caveat in the row; publish the caveat too.
- **open** — not yet true or not yet measured; do not publish as a capability.
- **to cite** — a competitor's figure, which needs their published source before it is used.

## 1. NAM: more A2 models at once

| ID | Public wording (draft) | Number | Evidence | Status |
|---|---|---|---|---|
| C1 | Our NEON kernels make NAM's A2 Full about twice as fast on the Pi 5's CPU | 2.14× at 64-frame blocks (2.00–2.35× over 32–256) | `namchain/plan.md` (the PR #313 A/B table), `namchain/bench-results/pr313-planar-ab.csv`; upstream as NeuralAmpModelerCore PR #313 | measured |
| C2 | …and A2 Lite three times as fast | 3.01× at 64 (2.96–3.14×) | as C1 | measured |
| C3 | 9 full-quality A2 models on one core of a Raspberry Pi 5; 30 A2 Lite | 0.111 and 0.0333 of a core, p99 under the 1.33 ms deadline | `pedal.project/bench-results/2026-10-08-cost-table-vip/README.md`, `pedal.project/devices/vip/rootfs/etc/namchain/cost.json` | qualified: **per core**. vip isolates cores 1–3 for audio (`devices/vip/rootfs/etc/pedal/tune.conf`), but no whole-pedal count with warm rigs held has been measured. Do not multiply by three |
| C4 | Before the kernels, one core held 4 at half load; now 9 | 4 → 9 A2 Full at 50 % of the deadline | `namchain/plan.md`, same table | measured (piv, Cortex-A76, same SoC as vip) |
| C5 | Independently reproduced | >2× on Apple M1 and inside the NAM plugin, by a third party | `namchain/plan.md`, beside the table | to cite: link the third party's own post, with their permission |

## 2. Latency and switching

| ID | Public wording (draft) | Number | Evidence | Status |
|---|---|---|---|---|
| C6 | About 4 ms from the input jack to the output jack | 183 frames = 3.81 ms at 64-frame periods × 4; converters alone 1.15–1.18 ms | `pedal.project/docs/codec-bringup-2a.md` (results table, 2026-09-27) | qualified: measured on 2026-09-27 with `namchain-latency`; re-measure on vip's current configuration (periods, rig loaded) before publishing |
| C7 | Knob turns are ramped per sample; adding, removing or rewiring blocks crossfades between the old and new rig rendered side by side | mechanism | `namchain/docs/transitions.md` | measured (built and tested) |
| C8 | A switch to a ready rig hands over in about 9 ms, with no dropout | `handover_blocks: 3` + 5 ms fade; 0 xruns over 8 live switches | `pedal.project/docs/managing-processing-power-and-optimising-for-fast-switching.md`, T7 | qualified: engine-level. A press through `pedald` measured 108–110 ms, ~100 ms of it HTTP (same doc, T9) — don't say "9 ms from the footswitch" |
| C9 | Even a rig that isn't ready is heard within about 40 ms | Lite stand-in audible 41 ms after the press; Full at 320 ms | same doc, T9; `pedal.project/bench-results/2026-10-10-t9-lite-first/` | qualified: the replay that makes the Full sound right on arrival is **not achieved on the board**; the Full crossfades in from a cold start. Model swap inside a rig is crossfaded but not warm-started (`namchain/docs/transitions.md`, M3) |
| C10 | An hour of playing and switching: zero dropouts. Two absurd stacked-amp rigs, edited and switched live: zero glitches | 0 xruns (T10); 0 xruns, DSP 73 % (2026-10-13) | cost-table README above (T10); `pedal.project/plan.md` 2026-10-13, `pedal.project/bench-results/2026-10-13-two-heavy-rigs-playtest.png` | measured |

## 3. Audio quality

| ID | Public wording (draft) | Number | Evidence | Status |
|---|---|---|---|---|
| C11 | With a guitar plugged in, the input stage adds 1.5 dB(A) to the converter's own noise | −86.53 dBFS, −89.92 dBFS(A) (run 31) | `pedal.project/plan.md` 2026-10-13; `pedal.project/noise-tests/` | qualified: one run on the corrected board; repeat before publishing |
| C12 | Converter noise floor | ADC −93.5 dBFS(A) (≈21 µV), input shorted | `pedal.project/docs/codec-bringup-2a.md` | measured |
| C13 | Flat from 20 Hz to 20 kHz | DAC within 0.1 dB; ADC −1.7 dB at 20 kHz from a test source | same | qualified: say "DAC flat within 0.1 dB"; the ADC figure includes the source |
| C14 | Low distortion | DAC THD −80 to −82 dB; ADC THD −72 dB at −1 dBFS | same | measured — modest next to studio converters; publish as numbers, not adjectives |
| C15 | The hum that remains comes from the host's mains supply, and we know why | 28 dB of 50 Hz from a mains brick vs a battery | `pedal.project/bench-results/2026-10-13-input-hum-and-the-host-supply.md` | open: the fix (isolated supply, or the Cioks) is not measured yet. Material for a "how we measure" page, not a headline |

## 4. Hardware and open designs

| ID | Public wording (draft) | Number | Evidence | Status |
|---|---|---|---|---|
| C16 | Built from standard parts: Raspberry Pi 5, Raspberry Pi Pico 2, a WM8960 codec board, through-hole analogue stages | — | `pedal.project/docs/hardware-handoff.md`, `pedal.project/docs/bom.md` | measured. Note the SparkFun WM8960 board is retired: say what replaces it |
| C17 | The build parts for the analogue boards cost about £120 | £117.19 ex VAT, 41 lines | `pedal.project/docs/bom.md`, "Total" | qualified: excludes the Pi, Pico, codec, case and screen. A whole-unit cost is **open**; work it out before any "a fraction of the price" line |
| C18 | Schematics generated from wiring tables and checked against KiCad's netlist; board layouts as data, checked against the netlist | — | `pedal.project/schematic/`, `pedal.project/stripboard/` | measured |
| C19 | The software image is built reproducibly from pinned commits; a bad kernel falls back by itself | — | `pedal.project/docs/vip-image.md`, `rtpi/README.md` | measured |
| C20 | Each circuit is its own pluggable board, testable and replaceable alone | — | `pedal.project/docs/modules.md` | open: a proposal (2026-10-11), not built |

## 5. Comparisons with commercial units

"Rivals" and "surpasses" need a competitor's own published figure and ours measured the same way.
None is cited yet; these are the comparisons worth making, and what each needs.

| Dimension | Ours | Compare against | Needs |
|---|---|---|---|
| Simultaneous neural captures | C3 | Units that run captures or NAM (e.g. Neural DSP Quad Cortex, IK Multimedia TONEX, Line 6 Helix Stadium) | Their published limits; whether they run NAM at all, and at which architecture |
| Switch gap | C8, C9 | Published switching gap / spillover behaviour of the same units, Fractal, Kemper, HeadRush | Their specs or a reputable measurement; ideally ours and theirs on one rig of recording gear |
| Round-trip latency | C6 | Published latency figures | Same measurement method (analogue in to analogue out) |
| Price | C17 (open) | Street price | A whole-unit BOM cost |
| Openness and repair | C16, C18, C19 | All of them | No number: this is the one "surpasses" that holds without measurement |
