# The message

What the website and the video both say. Written 2026-10-19 from the owner's brief; the wording here
is a draft to argue with, not a decision.

## What the pedal project enables

**An open-source, open-design effects unit for guitar, bass and vocals, with capabilities that rival
— and in places surpass — commercial units costing several times as much.** Every line of software,
every circuit, every board layout and every measurement is public, so anyone can build one, change
one, or build them for other people.

It is not a product in a box. It is the whole recipe for one, and a working instance of it.

## Who it is for

1. **Players** who want what a high-end modeller does — neural amp captures, cabinet IRs, big rigs,
   instant switching — and are curious about, or already use, NAM.
2. **Builders**: people who make pedals for themselves or sell a few, and want a design they can
   source, solder, case and repair, with the reasoning written down.
3. **Developers and the NAM community**: people who would use, extend or reuse the engine, the NEON
   kernels, the real-time Linux setup or the rig designer.

The website serves all three from the first page and splits them after it. The video is for the
first group and pulls the other two in at the end.

## The four things it shows off

These are the owner's four, in the owner's order. Each has a one-line promise, the proof we can
show, and the honest edge of that proof. The numbers are in [claims.md](claims.md).

### 1. More of the best NAM models, at once

- **Promise:** run many full-quality NAM A2 models at the same time, on a board that costs less than
  a pedal.
- **Proof:** hand-written NEON kernels for NAM's A2 WaveNet, submitted upstream to
  NeuralAmpModelerCore, make it 2.1× faster for A2 Full and 3× for A2 Lite on the Pi 5's
  Cortex-A76. Measured on the pedal's own board: **9 A2 Full models on one core**, 30 A2 Lite.
- **Edge:** per core, not per pedal; the whole-pedal figure depends on how many cores render (C3).

### 2. Inaudible changes, even whole rigs

- **Promise:** turn a knob, add a block, swap an amp, or change the whole rig — and hear the new
  sound, never a gap, click or dropout.
- **Proof:** parameter changes are ramped per sample; structural edits render old and new side by
  side and crossfade; the engine hands over to a pre-loaded rig in about 9 ms. An hour of
  playing and switching produced zero dropouts, and two deliberately absurd stacked-amp rigs were
  switched and edited live with zero glitches.
- **Low latency underneath it:** 64-sample blocks at 48 kHz (1.3 ms each); about 3.8 ms measured
  from the input jack to the output jack.
- **Edge:** a cold switch (a rig not held ready) is audible about 41 ms after the press, with a
  lighter model standing in until the full one is ready; the step that makes the full model
  sound right the instant it lands is not yet working on the board (C9). And a press through the
  pedal service today adds about 100 ms of HTTP round trip before the engine's 9 ms (C8): the
  switch is seamless, but not yet instant from the footswitch.

### 3. Excellent audio quality

- **Promise:** a quiet, clean path, measured and published at every stage.
- **Proof:** the input chain, with a guitar plugged in, adds 1.5 dB(A) to the codec's own floor;
  the converters are flat to 0.1 dB across 20 Hz–20 kHz.
- **Edge:** the converter today is a low-cost codec board, and the remaining hum comes from the
  host's mains supply, a measured, understood and open item. The pitch is *measured and honest*,
  and *the converter is a module you can swap*, not "studio grade" until it is (C11–C15).

### 4. Hardware you choose, designs you can build

- **Promise:** standard, affordable parts — a Raspberry Pi 5, a Pico 2, a codec board, through-hole
  analogue stages — with every design open, so you can build one for yourself or for others.
- **Proof:** schematics generated from wiring tables and checked against KiCad's netlist; board
  layouts as data, checked against the netlist; a bill of materials with part codes; a card image
  built reproducibly from pinned commits; a real-time kernel with a boot that falls back by itself.
- **Edge:** the modular board set is a proposal; the case layout is not designed yet (C16–C20).

### Around the four

These are not the headline, but they are what makes the four usable, and both artefacts show them:
**ljoss**, the rig designer on Mac, iPhone and iPad, editing the pedal live over Wi-Fi; **rigpa**,
the pedal's own touchscreen UI; footswitches and MIDI that produce identical events.

## Tone

- **Show, then say.** Audio first, number second, explanation third.
- **Specific.** "9 A2 Full models on one core of a Pi 5" beats "incredible performance".
- **Honest about the edges.** A claim with its status earns more trust from builders and NAM
  developers than a claim without one, and they are the people who would check.
- **Credit.** NAM is Steven Atkinson's project and its community's; captures are their authors'.
  The pedal builds on them and says so.
- **No hype words** without a number beside them: "rivals", "surpasses", "studio", "pro".

## What it is called

Open (see the website outline's open decisions). "pedal" is the working name; the repositories'
names (namchain, ljoss, rigpa, rtpi) are internal and should not lead.
