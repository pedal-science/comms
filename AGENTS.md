# comms

How the pedal is shown to people who are not building it: the website and the video. This repo
holds their outlines, their sources as they are made, and every asset they use.

This file is canonical for every agent; `CLAUDE.md` only imports it. The pedal as a system is
`../pedal.project/AGENTS.md`, and `../pedal.project/docs/working-across-repos.md` says which
repository owns what. This repo owns **no technical fact**: it owns the public wording of facts
that live elsewhere.

## What is here

| Path | What it is |
|---|---|
| `docs/message.md` | What the pedal enables, who it is for, the four things it shows off, and the tone |
| `docs/claims.md` | Every number or claim the website or video makes, with the evidence it rests on |
| `website/outline.md` | The site: its map, the first page (the overview) in detail, and what comes later |
| `video/outline.md` | The video: its structure, scenes, shots, a draft narration, and how it is recorded |
| `assets/` | Footage, audio, renders and photos, once made (see `assets/README.md`) |

## Rules

- **The public name is pedal.science**, at `pedal.science`. All the repositories will be public
  before the site links to them.
- **Every claim goes through `docs/claims.md`.** The site and the video use its public wording; the
  evidence and internal notes beside it are for us. If the evidence moves on, the register changes
  first and the site and video follow it.
- **The NAM numbers are the Raspberry Pi 5's.** Mac figures are not the target and are not used.
- **No latency figures and no rig sizes** are quoted with the switching claim; its wording is
  "extremely low latency switching, even of a fully loaded rig; no audible switching artefacts, no
  dropouts".
- **"Surpasses" is said of two things only**: more NAM and IR per rig than any product on the
  market, and low-latency switching at that load without dropouts or artefacts. It is the owner's
  assessment; `docs/claims.md` section 5 tracks the comparison that would substantiate it, and
  publishing does not wait on it.
- **It is not a product**: no prices, nothing for sale, no sales language.
- **Captures and IRs** heard are publicly available; credit their authors. Don't commit the `.nam`
  or IR files themselves here — link to where they are published.
- **The audio in the video is the pedal's own output**, recorded at the jack, and is not edited
  across a switch.
- **Hardware is shown from the 3D model** of the current enclosure (Hammond 1456RH3) and its 8.8″
  screen, which lives in `pedal.project/enclosure/`; comms holds only its renders.
- No brand marks of competitors beyond naming them.
- Commit to `main`; pushes wait for the owner's say-so.
