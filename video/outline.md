# The video: outline

**About 3½ minutes**, for players first, with builders and developers pulled in at the end. It says
what [../docs/message.md](../docs/message.md) says, in the same order, and every number on screen is
a row in [../docs/claims.md](../docs/claims.md). It is also the source of the website's hero loop and
its "hear the switch" clip, so those are shot with it.

## The rule that makes it work

**What you hear is the pedal's output, recorded at the jack, and nothing is edited across a
switch.** Picture can cut; audio across a rig change cannot. Say so on screen once (scene 3). If a
take has a glitch, it is reshot or the glitch is shown and explained, never patched.

## Structure

| # | Scene | Time | What happens | Claims |
|---|---|---|---|---|
| 1 | Cold open | 0:00–0:20 | Playing, close on hands. Mid-phrase, a stomp: the sound changes completely — clean to a stacked high-gain rig — with no gap. Again, to something absurd. No narration | C10 |
| 2 | Title | 0:20–0:30 | The name. Sub-line: "An open-source effects unit for guitar, bass and vocals. Build one." | — |
| 3 | What it is | 0:30–0:55 | Narrated over the pedal, the boards and the rig designer: neural captures of real amps, a Raspberry Pi, everything published. On-screen: "Audio in this video: the pedal's output, unedited across switches" | C16 |
| 4 | More models | 0:55–1:30 | A rig being built in the designer, block by block, amps stacked into amps. The engine's own CPU meter on screen as it grows. The number: 9 full-quality models on one core. A quick chart: before and after the NEON kernels | C1–C4 |
| 5 | Seamless | 1:30–2:10 | Three beats: a knob swept while playing (ramped); a block dragged into the chain while playing (crossfaded); whole rigs switched mid-phrase, with the output waveform drawn underneath so the switch point is visible and the audio shows no join. Then the latency line, about 4 ms jack to jack | C6–C8, C10 |
| 6 | Clean | 2:10–2:35 | Silence test: guitar plugged in, volume up, not playing — the noise meter. Then the measurement page, briefly: "every measurement is published". The +1.5 dB(A) number | C11, C12 |
| 7 | Yours | 2:35–3:10 | Hardware tour: the Pi 5, the Pico 2, the codec board, the input and output boards, the case. The schematic, the board layout drawn from data, the bill of materials scrolling. "Build one for yourself, or for others" | C16–C19 |
| 8 | Status and invitation | 3:10–3:30 | Honest and short: what plays today, what's next (the screen, footswitches, the case). Where to go: the website, the repositories. Credits: NAM and its community, the capture authors heard | — |

The order is the owner's four pillars, with the switch moved to the cold open as well: it is the
thing a player feels in five seconds, and it needs no explanation.

## Draft narration

Plain, first person, unhurried. About 330 words for 3½ minutes with room for music to breathe.

> **(3)** This is a guitar effects unit — for bass and vocals too — and you can build one. It runs
> neural captures of real amps and cabinets on a Raspberry Pi. Every line of its software, every
> circuit and every measurement is public.
>
> **(4)** The amp models are NAM — Neural Amp Modeler — at its highest quality. Running them fast
> enough on a small computer is the hard part, so I rewrote the core of NAM's processing for this
> processor, and offered it back to the NAM project. It runs these models two to three times faster.
> One core of this Pi now runs nine of them at once.
>
> **(5)** Changing sound should never cost you a note. Turn a knob and the change is smoothed sample
> by sample. Add an effect and the pedal runs the old rig and the new one side by side, and fades
> between them. Change the whole rig, and you hear… the new rig. An hour of playing and switching:
> not one dropout. And from the input jack to the output, about four milliseconds.
>
> **(6)** It's quiet. With a guitar plugged in, the input adds almost nothing to the converter's own
> noise — and every measurement behind that is published, including the ones that went wrong.
>
> **(7)** It's made from parts you can buy: a Raspberry Pi 5, a Pico for the footswitches and MIDI,
> a codec board, and analogue boards you can solder yourself. The schematics, the board layouts and
> the parts list are all open — build one for yourself, change it, or build them for other people.
>
> **(8)** It plays today. The screen, the footswitches and the case are next. Everything is at
> [site]. This is built on Neural Amp Modeler, by Steven Atkinson and its community, and on the
> captures of the people credited below. Thank you.

The narration says nothing the claims register does not support as worded; if a number changes, the
line changes.

## Shot list

| Shot | Scenes | Kit | Notes |
|---|---|---|---|
| Hands playing, close | 1, 5 | camera on a stand, shallow focus | Footswitch in frame for the stomp. Until footswitch hardware exists, the switch is triggered from the designer or rigpa — show that honestly |
| The pedal, wide and detail | 2, 3, 7 | camera, soft light | Inside and outside the case; the boards out of the case on a mat |
| Rig designer screen recording | 4, 5 | iPad / Mac screen capture | ljoss building the stacked rig; rigpa over VNC or on its screen once fitted |
| Engine meter | 4 | screen capture | The engine's own DSP/health panel as models are added (as in `pedal.project/bench-results/2026-10-13-two-heavy-rigs-playtest.png`) |
| Output waveform | 1, 5 | rendered from the recording | Drawn from the pedal's recorded output, synced to picture; the switch point marked |
| Noise meter | 6 | screen capture of a live analyser, or the published noise page | Guitar plugged in, volume up, not played |
| Schematic, layout, BOM | 7 | screen capture / rendered stills | From `pedal.project/schematic/renders/`, `pedal.project/stripboard/`, `pedal.project/docs/bom.md` |
| NEON before/after chart | 4 | motion graphic | From C1–C4's numbers only |

## Audio capture

- Record the pedal's output **and** the DI at the same time, at 48 kHz, onto a separate recorder or
  interface, so the DI can be shown and the output can be checked sample by sample around every
  switch.
- Log for every take: the rig documents, the engine commit (`/opt/namchain/<commit>`), the models
  and IRs, and `engine.status` before and after (xruns, guard trips). Kept beside the audio in
  `assets/audio/`.
- The rigs: two or three, chosen to sound as different as possible, each built only from captures
  and IRs whose authors have given permission to publish.
- The playing: one player, short phrases with sustain across the switch point, where a gap would be
  most audible.

## Production

1. **Lock the claims.** Re-measure C6 and repeat C11 on the current pedal; resolve every row the
   video uses to *measured* or *qualified* with its caveat spoken or on screen.
2. **Pick the rigs and clear the captures.**
3. **Shoot**: audio-first takes for scenes 1 and 5, then picture.
4. **Screen recordings and graphics.**
5. **Narration**, recorded after the edit is locked to picture.
6. **Edit**, with the rule above checked on every switch.
7. **Review against `docs/claims.md`**, then publish on the site and a video platform.

## Open decisions (the owner's)

1. **Who is on camera and whose voice** — the owner's, presumably; it is a first-person story.
2. **Shoot now or after the case and footswitches?** Recommended: shoot scenes 1 and 5 after the
   footswitches work, because a stomp is worth more than a tap on a screen; everything else can be
   shot now. A shorter "work in progress" cut is possible today.
3. **Music**: none under playing (the pedal is the music); a quiet bed under scene 7 at most,
   licensed.
4. **Where large files live**: Git LFS in this repo, or outside it with a manifest in `assets/`.
5. **Platform and length variants**: a 3½-minute main cut, plus a 30-second cut (scenes 1, 4, 5's
   switch, title) for social posts.
6. **Animated graphics tool**: a code-driven one (e.g. Motion Canvas or Remotion) keeps the charts
   tied to the numbers in `docs/claims.md`; a conventional editor is quicker for one video.
