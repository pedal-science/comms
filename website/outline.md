# The website: outline

The site will eventually describe the whole pedal project. **Version 1 is one page: the overview.**
Everything else on the map below is listed so v1 leaves room for it, not built. What the site says
is [../docs/message.md](../docs/message.md); every number on it is in
[../docs/claims.md](../docs/claims.md).

## The map

| Page | In v1? | For | What it holds |
|---|---|---|---|
| **Overview** (`/`) | **yes** | everyone | Below, in detail |
| Hear it | later | players | Rigs played through the pedal: DI and output side by side, switches left unedited |
| NAM, faster | later | developers, NAM community | The planar NEON kernels: what changed, the benchmarks, how to reproduce them, the upstream PR |
| Switching | later | players, developers | How a whole-rig change stays silent: ramps, dual-render crossfades, warm rigs, the Lite stand-in |
| Audio quality | later | builders | The measurement method, every noise and distortion run, the hum investigation, published as it was |
| Build one | later | builders | Parts, boards, schematics, the case, the card image, step by step |
| The software | later | developers | namchain, ljoss, rigpa, rtpi, `pedald`: what each is, its repo, how they talk |
| Status | later | everyone | What works, what is open, from `pedal.project/plan.md` |
| The video | when made | everyone | Embedded on the overview too |

## The overview page, section by section

Each section: what it says, what's on screen, and the claims it uses.

### 1. Hero

- **Headline (draft):** "An effects unit you can build. Open from the code to the circuit boards."
- **Sub-line:** guitar, bass and vocals; neural amp models (NAM) and IRs; capabilities that rival
  units costing several times as much.
- **Visual:** the video's opening ten seconds as a muted loop, or a still of the pedal being played,
  until the video exists. Play button opens the video.
- **Calls to action:** *Watch the video* · *See the designs* (GitHub).

### 2. What it is, in three sentences

Plain words for a player who has never heard of NAM: a Raspberry Pi runs neural captures of real
amps and cabinets; you design your rig on a phone, tablet or Mac, or on the pedal's own screen;
everything — software, schematics, board layouts, measurements — is published so anyone can build
or change it.

### 3. The four pillars

Four cards, each with a headline number, one sentence, and a "how" link to its later page (inert in
v1, or pointing at the repo doc until the page exists).

| Card | Headline | Sentence | Claims |
|---|---|---|---|
| More models | **9** full-quality NAM models on one core | Hand-written NEON kernels make NAM's A2 models 2–3× faster on the Pi 5, contributed upstream | C1–C4 |
| Seamless | **0** dropouts in an hour of playing and switching | Edits are ramped; rig changes render both rigs and crossfade, so you never hear the join | C7, C8, C10 |
| Clean | **+1.5 dB(A)** over the converter's own floor | The input stage, with a guitar plugged in, adds almost nothing; every measurement is published | C11, C12 |
| Yours | **Open** designs, standard parts | Pi 5, Pico 2, a codec board, through-hole analogue boards: build one, repair one, build them for others | C16, C18, C19 |

Latency (C6, about 4 ms jack to jack) sits under the Seamless card as a second line, once
re-measured.

### 4. Hear the switch

A short audio player (or the relevant clip of the video): one take, two rigs as different as
possible, switched mid-phrase, with the waveform drawn under it so the eye can find the switch and
the ear can't. Caption: the take is unedited, recorded at the pedal's output. The single most
persuasive thing on the page, so it goes high.

### 5. How it fits together

One diagram: guitar → input board → codec → Pi 5 (engine on isolated real-time cores; the pedal
service; the touchscreen UI) → codec → outputs; the Pico 2 with footswitches, MIDI and controls,
over UART; ljoss on an iPad over Wi-Fi. Exported from `pedal.project/docs/diagrams/`, not redrawn
here, with a simplified "public" layer if the engineering diagram is too dense.

### 6. Honest status

A short, dated box: what plays today (the pedal plays heavy rigs, edited live and switched, C10)
and what is not done (the screen, the footswitch hardware, the case layout, the open items in the
claims register). Builders trust this more than polish.

### 7. Where to go

Links to the repositories with one line each, the licence(s), and how to follow the project.

### 8. Credits

NAM and its author and community; capture and IR authors heard on the page; the parts of the
project that stand on other open work (Linux PREEMPT_RT, Qt, the Raspberry Pi firmware).

## Design

- One column, readable on a phone first; dark by default (stage and studio light), light mode
  equal.
- Numbers set large in the cards; no stock photography — the pedal, the boards, the screen, hands
  playing.
- Diagrams as SVG so they stay sharp and searchable.

## How it is built and hosted (recommendation)

A static site, so it can be hosted for nothing and anyone can rebuild it: **Astro**, written in
Markdown with a few components (the pillar cards, the audio player with a waveform), built with
pnpm, published to **GitHub Pages** from this repo. No JavaScript is needed except the audio
player. The source goes in `website/` beside this outline.

## Open decisions (the owner's)

1. **The name.** "pedal" is the working name; the site needs a public one and a domain.
2. **Licences.** The software and the hardware designs each need one stated on the site (e.g. an
   OSI licence for the code, CERN-OHL for the hardware). Check what each repo carries today.
3. **Are the repositories public?** The site links to them; the ones that are private need opening
   or the links held back.
4. **Hosting and domain**: GitHub Pages under the owner's account, or a domain of its own.
5. **Comparisons on v1, or later?** Recommended later, on its own page, once section 5 of the claims
   register has cited figures.

## Before v1 goes up

- Re-measure C6 (latency) and repeat C11 (noise with a guitar) on the current pedal.
- Record the "hear the switch" take (shared with the video's shoot).
- Get permission, and credit, for every capture and IR heard.
- Read every row the page uses in `docs/claims.md` against its source again.
