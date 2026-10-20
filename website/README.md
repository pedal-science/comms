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

Type: the sidebar's title is Piazzolla 900 (Fontsource, `@fontsource/piazzolla`); everything else is
Lexica Ultralegible, whose four WOFF2 files and OFL licence are in
`public/fonts/lexica-ultralegible/`, copied from
[jacobxperez/lexica-ultralegible](https://github.com/jacobxperez/lexica-ultralegible) `fonts/web/`
at `198700e`. It has Regular and Bold only, so the CSS uses weights 400 and 700.
