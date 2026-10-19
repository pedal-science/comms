# The website: outline

**pedal.science**, at `pedal.science`. The site will eventually describe the whole project.
**Version 1 is one page: the overview.** Everything else on the map is listed so v1 leaves room for
it, not built. What the site says is [../docs/message.md](../docs/message.md); every claim on it is
in [../docs/claims.md](../docs/claims.md).

## The map

| Page | In v1? | For | What it holds |
|---|---|---|---|
| **Overview** (`/`) | **yes** | everyone | Below, in detail |
| Hear it | later | players | Rigs played through the pedal: DI and output side by side, switches left unedited |
| NAM and IR, faster | later | developers, NAM community | The NEON kernels and the IR convolver: what changed, the Pi 5 benchmarks, how to reproduce them, the upstream contributions |
| Switching | later | players, developers | How a whole-rig change stays silent: ramps, dual-render crossfades, warm rigs |
| Audio quality | later | builders | The measurement method and every run, published as it was |
| Build one | later | builders | Parts, boards, schematics, the enclosure and its 3D model, the card image, step by step |
| The software | later | developers | namchain, ljoss, rigpa, rtpi, `pedald`: what each is, its repo, how they talk |
| Status | later | everyone | What works and what is next, from `pedal.project/plan.md` |
| The video | when made | everyone | Embedded on the overview too |

## The overview page, section by section

### 1. Hero

- **Headline (draft):** "An effects unit you can build. Open from the code to the circuit boards."
- **Sub-line:** guitar, bass and vocals; neural amp models (NAM) and IRs; capabilities that rival —
  and in places surpass — commercial units.
- **Visual:** a render of the 3D model — the Hammond sloped console with the 8.8″ screen showing
  rigpa — slowly turning, until the video exists; then the video's opening as a muted loop. Play
  button opens the video.
- **Calls to action:** *Watch the video* · *See the designs* (GitHub).

### 2. What it is, in three sentences

For a player who has never heard of NAM: a Raspberry Pi 5 runs neural captures of real amps and
cabinets; you design your rig on a phone, tablet or Mac, or on the pedal's own touchscreen;
everything — software, schematics, board layouts, the enclosure, measurements — is published so
anyone can build or change it.

### 3. The four pillars

Four cards, each a headline, one sentence, and a "how" link to its later page (pointing at the repo
doc until the page exists).

| Card | Headline | Sentence | Claims |
|---|---|---|---|
| More models | **9** full-quality NAM models on one core of a Raspberry Pi 5 | Hand-written NEON kernels make NAM's A2 models 2–3× faster on the Pi 5, and long IRs a fraction of the cost — contributed back to NAM | C1–C5 |
| Seamless | **Extremely low latency switching**, even of a fully loaded rig | No audible switching artefacts, no dropouts | C6, C7 |
| Excellent audio | **Excellent audio quality** | A clean signal path, with every measurement published | C8 |
| Yours | **Open** designs, standard parts | Pi 5, Pico 2, a codec board, analogue boards you can solder: build one for yourself, or for others | C9–C11 |

### 4. Further than what's on the market

Two short statements, from [../docs/message.md](../docs/message.md):

- More NAM and IR per rig than any product on the market supports today. The optimisations are
  public, so others can catch up — but their code and designs aren't open, and these are.
- Low-latency switching at that load, without dropouts or audible artefacts.

No comparison table on v1; the "Switching" and "NAM and IR" pages carry the comparisons when
[../docs/claims.md](../docs/claims.md) section 5 has them.

### 5. Hear the switch

A short audio player (or the clip from the video): one take, two rigs as different as possible,
switched mid-phrase with a stomp, with the waveform drawn under it so the eye can find the switch
and the ear can't. Caption: unedited, recorded at the pedal's output. Added when the stomp scenes are
shot (after the footswitches work); until then the section is left out, not faked.

### 6. The hardware

The 3D model, exploded: the enclosure, the screen, the Pi 5, the Pico 2, the codec, the input and
output boards, the footswitches. Each part labelled with what it does. Beside it, one system diagram:
guitar → input board → codec → Pi 5 (the engine on isolated real-time cores, the pedal service, the
touchscreen UI) → codec → outputs; the Pico with footswitches, MIDI and controls over UART; ljoss on
an iPad over Wi-Fi. The diagram is exported from `pedal.project/docs/diagrams/`, not redrawn; the
renders come from `pedal.project/enclosure/` (claim C12).

### 7. Status

A short, dated box: what plays today (heavy rigs, edited live and switched) and what is next (the
case, the screen, the footswitches).

### 8. Where to go

The repositories with one line each, the licences, and how to follow the project.

### 9. Credits

NAM, Steven Atkinson and its community; the authors of the captures and IRs heard; the open work the
project stands on (Linux PREEMPT_RT, Qt, the Raspberry Pi firmware).

## Design

- One column, phone first; dark by default, light mode equal.
- The 3D model carries the visuals: renders, not stock photography, until the real case is built;
  then photos of the real thing beside the renders.
- Diagrams as SVG.

## How it is built and hosted

A static site, so anyone can rebuild it: **Astro**, written in Markdown with a few components (the
pillar cards, the audio player with a waveform, a 3D viewer or turntable render), built with pnpm.
The source goes in `website/`.

**Hosted on Cloudflare as a Worker with static assets**, deployed by Workers Builds from this repo
on GitHub (the dashboard's "Create an app" flow, not legacy Pages — Cloudflare recommends Workers
for new projects and puts new features there):

- **Root directory** `website/`, where `wrangler.jsonc` lives with `assets.directory` pointing at
  Astro's `./dist`. No Worker script for a static site; add a `main` script later if something
  dynamic is needed, in the same project.
- **Build watch paths** `website/**`, so commits to the outlines and docs don't redeploy the site.
- **Preview builds** on: each branch gets its own preview URL.
- **Custom domain** `pedal.science` attached to the Worker.
- **Video and large media are not static assets** (25 MiB per file): the video goes on Cloudflare
  Stream or a video platform, and big renders or audio in R2 if needed.

A live 3D viewer (e.g. `<model-viewer>` with a glTF export of the model) is worth it in the hardware
section; the hero uses a pre-rendered loop, which loads faster.

## Decided (2026-10-19)

- Name and domain: **pedal.science**.
- All the repositories are public, in the `pedal-science` GitHub org; the site links to them.
- Licence: **MIT** for every repository, software and hardware designs alike (a `LICENSE` file at
  each repository's top level).
- Publishing does not wait on re-measurement or comparisons.
- The 3D model of the new enclosure and screen is used on the site.

## Still open

1. **The panel layout.** The 3D model exists (`pedal.project/enclosure/`, the console model) and the
   site uses its renders, but its control positions are provisional until the layout is designed
   (claim C12); re-render when it is.
