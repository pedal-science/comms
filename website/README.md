# pedal.science — the website

An Astro static site, deployed by Cloudflare Workers Builds as the Worker `pedal-science-website`
(static assets only; `wrangler.jsonc`). What it says is [outline.md](outline.md); every claim on it
is in [../docs/claims.md](../docs/claims.md).

```sh
pnpm install --frozen-lockfile
pnpm dev        # Astro's dev server
pnpm preview    # build, then serve dist/ as Cloudflare will (wrangler dev)
```

Cloudflare's build settings: root directory `website`, build command
`pnpm install --frozen-lockfile && pnpm build`, deploy command `npx wrangler deploy`, build watch
path `website/**`. The `name` in `wrangler.jsonc` must match the Worker's name in the dashboard.
pnpm's version comes from `packageManager`, Node's from `.node-version`.

`public/renders/` are JPEG copies of `pedal.project/enclosure/renders/console_*.png` from
pedal.project `8792bae`. Re-export them from there when the model changes; never edit them here.

Type: DM Sans for text and DM Mono for labels, captions and identifiers, both from Fontsource
(`@fontsource/dm-sans`, `@fontsource/dm-mono`, SIL OFL 1.1). `Base.astro` imports only the weights
used: Sans 400 and 700 with their italics, Mono 400 and 500. The look follows the Creative Commons
site's design language; [outline.md](outline.md), "Design", says what that means here.

Colours: [src/palette.json](src/palette.json) holds every colour in both modes, and
`src/palette.ts` turns it into CSS in the page's head. To try colours out, press **Alt+Shift+P**
(Option+Shift+P on a Mac) on any page, or add `?palette` to the address: a small window lists the
colours of the mode on screen, each with a picker and a field that takes a hex colour, `transparent`
or another colour's name. The page changes as you edit. Use the site's theme switch (or the window's
Light/Dark buttons) to edit the other mode; edits to both are kept. **Download** saves a new
`palette.json` with both modes, to put over `src/palette.json` and commit. Edits live only in that
browser (localStorage) until then, survive a reload, and are dropped once the file agrees with them;
**Reset** discards them. The window can be dragged by its title bar and resized from its corner, and
Escape or the same keys close it. It ships with the site but loads only when asked for, and changes
only the viewer's own browser.
