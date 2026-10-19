# The video: outline

**pedal.science, about 3½ minutes**, for players first, with builders and developers pulled in at
the end. It says what [../docs/message.md](../docs/message.md) says, in the same order, and every
claim in it is in [../docs/claims.md](../docs/claims.md). It is also the source of the website's
hero loop and its "hear the switch" clip.

## The rule that makes it work

**What you hear is the pedal's output, recorded at the jack, and nothing is edited across a
switch.** Picture can cut; audio across a rig change cannot. Say so on screen once (scene 3).

## Two shoots

- **The stomp shoot** — scenes 1 and 5 — **after the footswitches work** (decided 2026-10-19). A
  stomp is the point; a tap on a screen is not.
- **Everything else** can be made before that: the 3D model's renders, screen recordings, the
  graphics, the hardware on the bench.

## Structure

| # | Scene | Time | What happens | Claims |
|---|---|---|---|---|
| 1 | Cold open | 0:00–0:20 | Playing, close on hands and foot. Mid-phrase, a stomp: the sound changes completely — clean to a stacked high-gain rig — with no gap. Again, to something absurd. No narration | C6, C7 |
| 2 | Title | 0:20–0:30 | The 3D model turns into view; **pedal.science**. Sub-line: "An open-source effects unit for guitar, bass and vocals. Build one." | — |
| 3 | What it is | 0:30–0:55 | Narrated over the model coming apart into its parts, then the real boards and the rig designer. On screen: "Audio in this video: the pedal's output, unedited across switches" | C9 |
| 4 | More models | 0:55–1:30 | A rig being built in the designer, block by block, amps stacked into amps, IRs after them. The engine's own load meter on screen. On screen: "2× faster A2 Full, 3× faster A2 Lite — on a Raspberry Pi 5" and "8 full-quality NAM models at once on a Pi 5" | C1–C5 |
| 5 | Seamless | 1:30–2:10 | A knob swept while playing; a block dragged in while playing; then whole, fully loaded rigs switched mid-phrase with stomps, the output waveform drawn underneath so the switch is visible and the join isn't. On screen: "Extremely low latency switching, even of a fully loaded rig. No audible switching artefacts, no dropouts." | C6, C7 |
| 6 | Further than the market | 2:10–2:30 | Narration over the loaded rig and the switch: more NAM and IR per rig than any product on the market; switching that load without a trace; and open | message.md, "Where it surpasses" |
| 7 | Yours | 2:30–3:05 | The 3D model exploded and labelled: case, screen, Pi 5, Pico 2, codec, input and output boards, footswitches. Then the schematic, a board layout drawn from data, the bill of materials. "Build one for yourself, or for others." Audio quality said here, briefly, with the measurement pages on screen | C8–C12 |
| 8 | Invitation | 3:05–3:30 | pedal.science and the repositories. Credits: NAM and its community, the capture and IR authors heard | — |

## Draft narration

Plain, first person, unhurried. About 320 words.

> **(3)** This is a guitar effects unit — for bass and vocals too — and you can build one. It runs
> neural captures of real amps and cabinets on a Raspberry Pi 5. Every line of its software, every
> circuit and every measurement is public.
>
> **(4)** The amp models are NAM — Neural Amp Modeler — at its highest quality. Running them on a
> small computer is the hard part, so I rewrote the core of NAM's processing for this processor, and
> offered it back to the NAM project: twice as fast for the full models, three times for the light
> ones. This Pi now runs eight full models at once. Long cabinet IRs got the same
> treatment.
>
> **(5)** Changing sound should never cost you a note. Turn a knob and the change is smoothed sample
> by sample. Add an effect and the pedal runs the old rig and the new one side by side, and fades
> between them. Change the whole rig — even a fully loaded one — and you hear… the new rig. No
> dropouts. Nothing to hear but the change.
>
> **(6)** As far as I know, nothing you can buy runs this many neural models and IRs in one rig, or
> switches a rig this heavy this quickly without a trace. My optimisations are public, so others
> will catch up — but this one's code and designs are open too.
>
> **(7)** It's made from parts you can buy: a Raspberry Pi 5, a Pico for the footswitches and MIDI,
> a codec board, and analogue boards you can solder yourself. It sounds excellent, and every
> measurement behind that is published. The schematics, the board layouts, the enclosure and the
> parts list are all open — build one for yourself, change it, or build them for other people.
>
> **(8)** It's all at pedal.science. It's built on Neural Amp Modeler, by Steven Atkinson and its
> community, and on the captures of the people credited below. Thank you.

## Shot list

| Shot | Scenes | Source | Notes |
|---|---|---|---|
| Hands and foot playing, close | 1, 5 | camera on a stand | Stomp shoot only; footswitch in frame |
| 3D model: turntable, assembly, exploded and labelled | 2, 3, 7 | renders from `pedal.project/enclosure/` | The Hammond 1456RH3 and the 8.8″ screen showing rigpa; captioned as a design render until the real case is built |
| The real hardware on the bench | 3, 7 | camera, soft light | The boards out of the case, beside the model's exploded view |
| Rig designer screen recording | 4, 5 | iPad / Mac capture | ljoss building the stacked rig; rigpa on its screen or over VNC |
| Engine load meter | 4 | screen capture | The engine's own panel as models are added (as in `pedal.project/bench-results/2026-10-13-two-heavy-rigs-playtest.png`) |
| Output waveform | 1, 5 | rendered from the recording | Drawn from the pedal's recorded output, synced to picture |
| Schematic, layout, BOM | 7 | screen capture / stills | `pedal.project/schematic/renders/`, `pedal.project/stripboard/`, `pedal.project/docs/bom.md` |
| Pi 5 speed-up chart | 4 | motion graphic | C1–C3's Pi numbers only |

## Audio capture

- Record the pedal's output **and** the DI together at 48 kHz, on a separate recorder or interface,
  so the output can be checked around every switch.
- Log for every take: the rig documents, the engine commit, the models and IRs with their authors
  and where they are published, and `engine.status` before and after (xruns, guard trips). Kept in
  `assets/audio/`.
- Rigs: two or three, as different as possible and fully loaded. Switch between rigs held warm —
  which is what a press in a bank does (claims.md, C7's note).
- Playing: short phrases with sustain across the switch point, where a gap would be most audible.

## Production

1. Make the 3D model of the new enclosure and screen (claim C12), and render scenes 2, 3 and 7.
2. Screen recordings and graphics for scene 4.
3. Narration draft locked; a work-in-progress cut without scenes 1 and 5 is possible here.
4. **Stomp shoot**, once the footswitches work: scenes 1 and 5, audio first.
5. Narration recorded to the locked edit.
6. Edit, with the rule above checked on every switch.
7. Publish on pedal.science and a video platform; a 30-second cut (scenes 1, 4, 5's switch, title)
   for social posts.

## Decided (2026-10-19)

- Name: **pedal.science**.
- The stomp scenes are shot after the footswitches work.
- The 3D model of the new enclosure and screen is used for the hardware scenes.
- Captures and IRs are publicly available; their authors are credited.

## Still open

1. **Voice and face**: the owner's, presumably — it is a first-person story.
2. **Music**: none under playing; a quiet licensed bed under scene 7 at most.
3. **Where large files live**: Git LFS here, or outside the repo with a manifest in `assets/`.
4. **Graphics tool**: code-driven (Motion Canvas, Remotion) keeps charts tied to `docs/claims.md`;
   a conventional editor is quicker for one video. The 3D renders come from Blender either way,
   since the enclosure model is a Blender file.
