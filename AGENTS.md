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

- **Every claim goes through `docs/claims.md`.** A number on the site or in the video is the one in
  the register, which links to the bench result, document or commit it comes from. If the
  evidence moves on, the register changes first and the site and video follow it.
- **Measured, not hoped.** A claim whose evidence says "not achieved" or "open" is not made, or is
  made with that status, in words. "Rivals" and "surpasses" are said only against a competitor's own
  published figure, cited, measured the same way.
- **Nothing that is not ours to publish.** NAM captures and IRs are other people's work
  (`../NAMBench/nam-files/README.md`). A model heard in the video, or named on the site, has its
  author's permission or licence recorded beside the asset, and is credited.
- **The audio in the video is the pedal's own output**, recorded at the jack, and is not edited
  across a switch. The switching claim is only as good as that.
- **No brand marks of competitors** beyond naming them in a comparison with a citation.
- Commit to `main`; pushes wait for the owner's say-so.
