// The theme switch: `data-theme="light"` or `"dark"` on <html>, or none to follow the system. The
// choice is kept in localStorage; Base.astro's head script reads it back before the first paint.
export type Theme = 'light' | 'dark' | 'auto';

const KEY = 'pedal.theme';
const systemDark = matchMedia('(prefers-color-scheme: dark)');

export function theme(): Theme {
	const t = document.documentElement.dataset.theme;
	return t === 'light' || t === 'dark' ? t : 'auto';
}

/** The mode on screen: the theme, or the system's when the theme is auto. */
export function mode(): 'light' | 'dark' {
	const t = theme();
	return t === 'auto' ? (systemDark.matches ? 'dark' : 'light') : t;
}

export function setTheme(t: Theme): void {
	if (t === 'auto') delete document.documentElement.dataset.theme;
	else document.documentElement.dataset.theme = t;
	try {
		if (t === 'auto') localStorage.removeItem(KEY);
		else localStorage.setItem(KEY, t);
	} catch {
		// Storage can be blocked; the switch still works for this page.
	}
	dispatchEvent(new Event('themechange'));
}

/** Calls `f` when the theme or the system's mode changes. */
export function onThemeChange(f: () => void): void {
	addEventListener('themechange', f);
	systemDark.addEventListener('change', f);
}
