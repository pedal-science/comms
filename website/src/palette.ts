// The site's colours (palette.json) as CSS custom properties, one per colour: `page` is `--page`.
// Base.astro writes the page's own copy at build time; the palette tool writes its edits with the
// same function, so the two cannot disagree about how a value becomes CSS.
import source from './palette.json';

export type Mode = 'light' | 'dark';
export interface Colour {
	group: string;
	use: string;
	light: string;
	dark: string;
}
export interface Palette {
	about: string;
	colours: Record<string, Colour>;
}
/** One mode's values, by colour name. */
export type Values = Record<string, string>;

export const palette: Palette = source;

/** A value as CSS: another colour's name becomes its variable, so it follows that colour. */
function cssValue(value: string): string {
	return value in palette.colours ? `var(--${value})` : value;
}

function block(selector: string, values: Values, mode: Mode): string {
	const lines = Object.entries(values).map(([name, value]) => `\t--${name}: ${cssValue(value)};`);
	return lines.length ? `${selector} {\n${lines.join('\n')}\n\tcolor-scheme: ${mode};\n}\n` : '';
}

/**
 * The CSS for both modes. `data-theme` on <html> is the theme switch: absent means follow the
 * system. The page's own copy keeps light as the bare `:root` default. Overrides (`strong`) use
 * selectors that cannot match in the same mode and are more specific than the page's, so they win
 * wherever in the document they are.
 */
export function paletteCss(light: Values, dark: Values, strong = false): string {
	if (strong) {
		const r = 'html:root';
		return (
			block(`${r}[data-theme="light"]`, light, 'light') +
			wrap('light', block(`${r}:not([data-theme="dark"])`, light, 'light')) +
			block(`${r}[data-theme="dark"]`, dark, 'dark') +
			wrap('dark', block(`${r}:not([data-theme="light"])`, dark, 'dark'))
		);
	}
	return (
		block(':root', light, 'light') +
		wrap('dark', block(':root:not([data-theme="light"])', dark, 'dark')) +
		block(':root[data-theme="dark"]', dark, 'dark')
	);
}

function wrap(mode: Mode, css: string): string {
	return css && `@media (prefers-color-scheme: ${mode}) {\n${css}}\n`;
}

/** One mode's values from the file. */
export function values(mode: Mode): Values {
	return Object.fromEntries(Object.entries(palette.colours).map(([name, c]) => [name, c[mode]]));
}
