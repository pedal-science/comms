# The message

What the website and the video both say. Written 2026-10-19 from the owner's brief and revised the
same day with the owner's corrections.

## The name

**pedal.science** — the project's public name and its domain, `pedal.science`. The repositories'
names (namchain, ljoss, rigpa, rtpi) are internal and do not lead.

## What it enables

**An open-source, open-design effects unit for guitar, bass and vocals, with capabilities that rival
— and in places surpass — commercial units.** Every line of software, every circuit, every board
layout and every measurement is public, so anyone can build one, change one, or build them for
other people.

It is not a product, and nothing is for sale. It is the whole recipe for one, and a working instance
of it.

## Who it is for

1. **Players** who want what a high-end modeller does — neural amp captures, cabinet IRs, big rigs,
   instant switching — and are curious about, or already use, NAM.
2. **Builders**: people who make pedals for themselves or for others, and want a design they can
   source, solder, case and repair, with the reasoning written down.
3. **Developers and the NAM community**: people who would use, extend or reuse the engine, the NEON
   kernels, the real-time Linux setup or the rig designer.

The website serves all three from the first page and splits them after it. The video is for the
first group and pulls the other two in at the end.

## The four things it shows off

The owner's four, in the owner's order. The wording is the public wording; [claims.md](claims.md)
holds the evidence behind each.

### 1. More of the best NAM models, at once

- **Say:** NAM's A2 models run **2× faster (A2 Full) and 3× faster (A2 Lite)** on the Raspberry Pi
  5's processor, from hand-written NEON kernels contributed to NAM. **9 A2 Full models on one core
  of a Raspberry Pi 5**, or 30 A2 Lite. IRs too: the convolver behind them is faster at long IRs,
  also contributed.
- All headline numbers are the Pi 5's. Mac figures exist in NAMBench but are not the target and are
  not used.

### 2. Switching you can't hear

- **Say:** **Extremely low latency switching, even of a fully loaded rig. No audible switching
  artefacts, no dropouts.**
- No millisecond figures and no rig sizes are quoted with it.

### 3. Excellent audio quality

- **Say:** excellent audio quality, with the measurements published.
- No input-stage or noise figures in the headline.

### 4. Hardware you choose, designs you can build

- **Say:** standard, affordable parts — a Raspberry Pi 5, a Raspberry Pi Pico 2, a codec board,
  analogue boards you can solder — with every design open, so you can build one for yourself or for
  others.
- **Show:** the 3D model of the enclosure and its screen, the schematics, the board layouts, the
  bill of materials.

## Where it surpasses what's on the market

Two claims, the owner's own assessment. Both are said; neither waits on a comparison table, though
[claims.md](claims.md) section 5 tracks the quantitative comparison that would substantiate them.

1. **More NAM and IR per rig than any product on the market supports today.** The NAM and IR
   optimisations are public, so others will be able to catch up — but their code and designs are
   not open, and these are.
2. **Low-latency switching, at that load, without dropouts or audible artefacts.** No available
   product is known to switch rigs this heavy this fast without either.

## Around the four

Not the headline, but what makes the four usable, and both artefacts show them: **ljoss**, the rig
designer on Mac, iPhone and iPad, editing the pedal live over Wi-Fi; **rigpa**, the pedal's own
touchscreen UI on the 8.8″ screen; footswitches and MIDI that produce identical events.

## Tone

- **Show, then say.** Audio first, then the claim.
- **Specific where it is a number** (the NAM figures), plain where it is not (switching, audio).
- **Credit.** NAM is Steven Atkinson's project and its community's; captures and IRs are their
  authors'. pedal.science builds on them and says so.
- Not a product pitch: no prices, no "buy", no sales language.
