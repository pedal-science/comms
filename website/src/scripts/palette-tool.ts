// The palette tool: a small movable window over the site that edits src/palette.json's colours
// live, in whichever mode is on screen, and downloads the result as a new palette.json. Base.astro
// loads it on Alt+Shift+P (Option+Shift+P on a Mac) or ?palette. It changes only this browser's
// view: edits are kept in localStorage, and Base.astro's head script re-applies them on load, until
// they are reset or the file agrees with them.
//
// The window lives in a shadow root with fixed colours of its own, so no palette edit can make the
// tool itself unreadable.
import { palette, paletteCss, values, type Mode, type Values } from '../palette';
import { mode, onThemeChange, setTheme } from './theme';

const KEY = 'pedal.palette-tool';
const names = Object.keys(palette.colours);
const file: Record<Mode, Values> = { light: values('light'), dark: values('dark') };

interface State {
	open: boolean;
	edits: Record<Mode, Values>;
	left?: number;
	top?: number;
}

const state = load();
let host: HTMLElement | undefined;
let tool: HTMLElement;
const rows = new Map<string, Row>();

interface Row {
	el: HTMLLIElement;
	swatch: HTMLLabelElement;
	picker: HTMLInputElement;
	field: HTMLInputElement;
}

export function show(): void {
	if (!host) build();
	host!.hidden = false;
	state.open = true;
	place();
	refresh();
	save();
}

export function hide(): void {
	if (host) host.hidden = true;
	state.open = false;
	save();
}

export function toggle(): void {
	if (host && !host.hidden) hide();
	else show();
}

// --- State ---------------------------------------------------------------------------------------

function load(): State {
	try {
		const s = JSON.parse(localStorage.getItem(KEY) || 'null');
		if (s && typeof s === 'object') {
			return {
				open: s.open === true,
				edits: { light: clean(s.edits?.light, 'light'), dark: clean(s.edits?.dark, 'dark') },
				left: typeof s.left === 'number' ? s.left : undefined,
				top: typeof s.top === 'number' ? s.top : undefined,
			};
		}
	} catch {
		// Unreadable or blocked storage: start with no edits.
	}
	return { open: false, edits: { light: {}, dark: {} } };
}

/** Stored edits, less any to colours the file no longer has and any the file now agrees with. */
function clean(stored: unknown, m: Mode): Values {
	const out: Values = {};
	if (!stored || typeof stored !== 'object') return out;
	for (const [name, v] of Object.entries(stored)) {
		if (name in file[m] && typeof v === 'string' && v !== file[m][name]) out[name] = v;
	}
	for (const [name, v] of Object.entries(out)) {
		if (parse(v, name, m, { ...file[m], ...out }) === null) delete out[name];
	}
	return out;
}

/** Applies the edits to the page and keeps them, with the CSS the head script needs. */
function save(): void {
	const css = paletteCss(state.edits.light, state.edits.dark, true);
	let style = document.getElementById('palette-tool-edits');
	if (!style) {
		style = document.createElement('style');
		style.id = 'palette-tool-edits';
		document.head.append(style);
	}
	style.textContent = css;
	try {
		localStorage.setItem(KEY, JSON.stringify({ ...state, css }));
	} catch {
		// Storage blocked: the edits last until the page is closed.
	}
}

function current(m: Mode): Values {
	return { ...file[m], ...state.edits[m] };
}

function changes(): number {
	return Object.keys(state.edits.light).length + Object.keys(state.edits.dark).length;
}

function setValue(m: Mode, name: string, v: string): void {
	if (v === file[m][name]) delete state.edits[m][name];
	else state.edits[m][name] = v;
	save();
	refresh();
}

/**
 * A typed value as the file would hold it: a six-digit lower-case hex colour, `transparent`, or
 * another colour's name (as `accent`, `--accent` or `var(--accent)`). Null if it is none of those,
 * or names a colour that leads back to this one.
 */
function parse(input: string, name: string, m: Mode, within = current(m)): string | null {
	let v = input.trim().toLowerCase();
	const ref = /^(?:var\()?(?:--)?([a-z0-9-]+)\)?$/.exec(v);
	if (/^#[0-9a-f]{6}$/.test(v) || v === 'transparent') return v;
	if (/^#[0-9a-f]{3}$/.test(v)) return '#' + [...v.slice(1)].map((c) => c + c).join('');
	if (!ref || !(ref[1] in file[m]) || ref[1] === name) return null;
	v = ref[1];
	const seen = new Set([name]);
	for (let next = v; next in file[m]; next = within[next]) {
		if (seen.has(next)) return null;
		seen.add(next);
	}
	return v;
}

/** What a colour finally is, following names: a hex colour or `transparent`. */
function resolve(m: Mode, name: string): string {
	const values = current(m);
	let v = values[name];
	for (let i = 0; i < names.length && v in values; i++) v = values[v];
	return v;
}

function download(): void {
	const colours = Object.fromEntries(
		names.map((n) => [n, { ...palette.colours[n], light: current('light')[n], dark: current('dark')[n] }]),
	);
	const text = JSON.stringify({ about: palette.about, colours }, null, '\t') + '\n';
	const a = document.createElement('a');
	a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
	a.download = 'palette.json';
	a.click();
	setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// --- The window ----------------------------------------------------------------------------------

function h<K extends keyof HTMLElementTagNameMap>(
	tag: K,
	props: Partial<HTMLElementTagNameMap[K]> & Record<string, unknown> = {},
	...children: (Node | string)[]
): HTMLElementTagNameMap[K] {
	const el = Object.assign(document.createElement(tag), props);
	el.append(...children);
	return el;
}

function build(): void {
	host = h('div', { id: 'palette-tool' });
	const root = host.attachShadow({ mode: 'open' });
	root.append(h('style', { textContent: CSS }));

	const modeButtons = (['light', 'dark'] as const).map((m) =>
		h('button', { type: 'button', textContent: m === 'light' ? 'Light' : 'Dark', onclick: () => setTheme(m) }),
	);
	modeButtons.forEach((b, i) => (b.dataset.mode = i ? 'dark' : 'light'));
	const close = h('button', { type: 'button', className: 'close', textContent: '×', title: 'Close (Alt+Shift+P)', onclick: hide });
	close.setAttribute('aria-label', 'Close the palette tool');
	const modes = h('div', { className: 'modes' }, ...modeButtons);
	modes.setAttribute('role', 'group');
	modes.setAttribute('aria-label', 'Mode to edit');
	const header = h('header', {}, h('h2', { textContent: 'Palette' }), modes, close);

	const list = h('ol', { className: 'list' });
	let group = '';
	for (const name of names) {
		const c = palette.colours[name];
		if (c.group !== group) {
			group = c.group;
			list.append(h('li', { className: 'group', textContent: group }));
		}
		const picker = h('input', { type: 'color' });
		picker.setAttribute('aria-label', `${name}: pick a colour`);
		const swatch = h('label', { className: 'swatch' }, picker);
		const field = h('input', { type: 'text', className: 'value', spellcheck: false, autocomplete: 'off' });
		field.setAttribute('list', 'palette-names');
		field.setAttribute('aria-label', `${name}: a hex colour, transparent, or another colour’s name`);
		field.title = 'A hex colour, transparent, or another colour’s name to follow it';
		const revert = h('button', { type: 'button', className: 'revert', textContent: '↺', title: 'Back to the file’s value' });
		revert.setAttribute('aria-label', `Revert ${name}`);
		const el = h(
			'li',
			{ className: 'row' },
			swatch,
			h('div', { className: 'label' }, h('span', { className: 'name', textContent: name }), h('span', { className: 'use', textContent: c.use, title: c.use })),
			field,
			revert,
		);
		list.append(el);
		rows.set(name, { el, swatch, picker, field });

		picker.addEventListener('input', () => setValue(mode(), name, picker.value.toLowerCase()));
		field.addEventListener('input', () => {
			const v = parse(field.value, name, mode());
			field.toggleAttribute('aria-invalid', v === null);
			if (v !== null) setValue(mode(), name, v);
		});
		field.addEventListener('change', () => {
			field.removeAttribute('aria-invalid');
			field.value = current(mode())[name];
			refresh();
		});
		revert.addEventListener('click', () => setValue(mode(), name, file[mode()][name]));
	}
	const datalist = h('datalist', { id: 'palette-names' }, ...names.map((n) => h('option', { value: n })));

	const count = h('span', { className: 'count' });
	const reset = h('button', {
		type: 'button',
		className: 'reset',
		textContent: 'Reset',
		title: 'Discard every change, in both modes',
		onclick: () => {
			if (!changes() || !confirm('Discard every change to the palette, in both modes?')) return;
			state.edits = { light: {}, dark: {} };
			save();
			refresh();
		},
	});
	const save_ = h('button', {
		type: 'button',
		className: 'download',
		textContent: 'Download',
		title: 'Download palette.json, both modes, to save as website/src/palette.json',
		onclick: download,
	});
	const footer = h(
		'footer',
		{},
		h('div', { className: 'actions' }, count, reset, save_),
		h('p', { className: 'hint', textContent: 'Both modes. Save it as website/src/palette.json.' }),
	);

	tool = h('section', { className: 'tool' }, header, list, footer, datalist);
	tool.setAttribute('role', 'dialog');
	tool.setAttribute('aria-label', 'Palette tool');
	tool.addEventListener('keydown', (e) => {
		// A value field's own Escape closes its suggestions, not the window.
		if (e.key === 'Escape' && !(e.target as HTMLElement).matches('.value')) hide();
	});
	root.append(tool);
	document.body.append(host);

	drag(header);
	onThemeChange(refresh);
	addEventListener('resize', () => place());
}

/** Moves the window by its title bar, kept wholly on screen. */
function drag(handle: HTMLElement): void {
	let from: { x: number; y: number; left: number; top: number } | undefined;
	handle.addEventListener('pointerdown', (e) => {
		if (e.button !== 0 || (e.target as HTMLElement).closest('button')) return;
		const r = tool.getBoundingClientRect();
		from = { x: e.clientX, y: e.clientY, left: r.left, top: r.top };
		handle.setPointerCapture(e.pointerId);
		e.preventDefault();
	});
	handle.addEventListener('pointermove', (e) => {
		if (from) place(from.left + e.clientX - from.x, from.top + e.clientY - from.y);
	});
	const end = () => {
		if (from) save();
		from = undefined;
	};
	handle.addEventListener('pointerup', end);
	handle.addEventListener('pointercancel', end);
}

/** Puts the window at a position (by default where it was, or the bottom right), on screen. */
function place(left = state.left, top = state.top): void {
	const r = tool.getBoundingClientRect();
	const margin = 8;
	left ??= innerWidth - r.width - 16;
	top ??= innerHeight - r.height - 16;
	state.left = Math.round(Math.max(margin, Math.min(left, innerWidth - r.width - margin)));
	state.top = Math.round(Math.max(margin, Math.min(top, innerHeight - r.height - margin)));
	tool.style.left = `${state.left}px`;
	tool.style.top = `${state.top}px`;
}

/** Shows the mode on screen: every value, swatch and change mark. */
function refresh(): void {
	if (!host) return;
	const m = mode();
	const values = current(m);
	for (const [name, row] of rows) {
		const v = values[name];
		const shown = resolve(m, name);
		row.swatch.style.setProperty('--c', shown);
		if (shown.startsWith('#')) row.picker.value = shown;
		if (row.field !== host.shadowRoot!.activeElement) row.field.value = v;
		row.field.classList.toggle('alias', v in values);
		row.el.classList.toggle('changed', name in state.edits[m]);
	}
	for (const b of tool.querySelectorAll<HTMLButtonElement>('.modes button')) {
		b.setAttribute('aria-pressed', String(b.dataset.mode === m));
	}
	const n = changes();
	const here = Object.keys(state.edits[m]).length;
	tool.querySelector('.count')!.textContent = n ? `${n} changed, ${here} in ${m}` : 'No changes';
}

const CSS = `
:host { all: initial; }
.tool {
	position: fixed;
	z-index: 1000;
	display: flex;
	flex-direction: column;
	width: clamp(280px, 24vw, 360px);
	height: min(56vh, 560px);
	min-width: 260px;
	min-height: 240px;
	max-width: calc(100vw - 16px);
	max-height: calc(100vh - 16px);
	resize: both;
	overflow: hidden;
	background: #ffffff;
	color: #000000;
	border: 3px solid #000000;
	border-radius: 16px;
	box-shadow: 4px 4px 0 #adff00, 8px 8px 0 #000000;
	font: 400 13px/1.4 'DM Sans', system-ui, sans-serif;
}
button, input { font: inherit; color: inherit; }
button { cursor: pointer; }
:focus-visible { outline: 3px solid #2e1fb8; outline-offset: 1px; }

header {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 8px 8px 8px 12px;
	background: #000000;
	color: #ffffff;
	cursor: grab;
	touch-action: none;
	user-select: none;
}
header:active { cursor: grabbing; }
h2 { margin: 0 auto 0 0; font-size: 15px; font-weight: 700; }
.modes { display: flex; border: 2px solid #ffffff; border-radius: 60px; }
.modes button {
	border: 0;
	border-radius: 60px;
	padding: 2px 10px;
	background: transparent;
	font: 500 11px/1.4 'DM Mono', ui-monospace, monospace;
	text-transform: uppercase;
	letter-spacing: 0.02em;
}
.modes button[aria-pressed='true'] { background: #adff00; color: #000000; }
.close {
	width: 28px;
	height: 28px;
	border: 0;
	border-radius: 60px;
	background: transparent;
	font-size: 20px;
	line-height: 1;
}
.close:hover { background: #ff9cff; color: #000000; }

.list { flex: 1; overflow-y: auto; margin: 0; padding: 0 0 8px; list-style: none; }
.group {
	position: sticky;
	top: 0;
	z-index: 1;
	padding: 4px 12px;
	background: #f9f9f9;
	border-bottom: 1px solid #e0e0e0;
	font: 500 11px/1.4 'DM Mono', ui-monospace, monospace;
	text-transform: uppercase;
	letter-spacing: 0.04em;
}
.row {
	display: grid;
	grid-template-columns: 28px minmax(0, 1fr) 92px 20px;
	align-items: center;
	gap: 8px;
	padding: 4px 8px 4px 12px;
	border-bottom: 1px solid #e0e0e0;
}
.swatch {
	position: relative;
	width: 28px;
	height: 28px;
	border: 2px solid #000000;
	border-radius: 8px;
	background: linear-gradient(var(--c), var(--c)), repeating-conic-gradient(#cccccc 0 25%, #ffffff 0 50%) 0 0 / 8px 8px;
	cursor: pointer;
}
.swatch:has(:focus-visible) { outline: 3px solid #2e1fb8; outline-offset: 1px; }
.swatch input { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; border: 0; padding: 0; }
.label { display: flex; flex-direction: column; min-width: 0; }
.name { font: 500 12px/1.3 'DM Mono', ui-monospace, monospace; }
.changed .name::after { content: ' ●'; color: #2e1fb8; }
.use { color: #595959; font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.value {
	width: 100%;
	box-sizing: border-box;
	padding: 2px 6px;
	border: 2px solid #000000;
	border-radius: 8px;
	background: #ffffff;
	font: 400 12px/1.4 'DM Mono', ui-monospace, monospace;
}
.value.alias { font-style: italic; background: #f9f9f9; }
.value[aria-invalid] { border-color: #d40000; background: #ffd9cc; }
.revert {
	visibility: hidden;
	width: 20px;
	height: 20px;
	padding: 0;
	border: 0;
	border-radius: 60px;
	background: transparent;
	font-size: 14px;
}
.changed .revert { visibility: visible; }
.revert:hover { background: #ff9cff; }

footer { padding: 8px 12px; border-top: 3px solid #000000; }
.actions { display: flex; align-items: center; gap: 8px; }
.count { margin-right: auto; font: 400 11px/1.3 'DM Mono', ui-monospace, monospace; }
.reset, .download { border-radius: 60px; padding: 4px 12px; font-weight: 700; }
.reset { border: 2px solid #000000; background: #ffffff; }
.reset:hover { background: #ffd9cc; }
.download { border: 2px solid #000000; background: #000000; color: #ffffff; box-shadow: 2px 2px 0 #adff00; }
.download:hover { background: #2e1fb8; border-color: #2e1fb8; }
.download:active { transform: translate(2px, 2px); box-shadow: none; }
.hint { margin: 4px 0 0; color: #595959; font-size: 11px; }
`;
