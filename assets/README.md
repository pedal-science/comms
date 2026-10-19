# assets

Footage, audio, photos and renders for the website and the video. Empty until the shoot.

- `video/` — raw takes and the edit's exports. Large files go in Git LFS or outside the repo with a
  manifest here (decide before the first shoot; see `../video/outline.md`, "Open decisions").
- `audio/` — the pedal's own output, recorded at the jack, with the DI beside it. Each recording
  gets a `.md` naming the rig, the engine commit, and the models and IRs used, with their authors
  and where they are published.
- `photos/` — the hardware, the boards, the case.
- `renders/` — stills and animations from the enclosure's 3D model, which lives in
  `../pedal.project/enclosure/`; each names the model's commit.
- `diagrams/` — exported from the sources in `../pedal.project/docs/diagrams/` and
  `../pedal.project/schematic/`; never redrawn by hand here.

A model or IR heard in any recording is credited to its author; the files themselves are linked, not
committed.
