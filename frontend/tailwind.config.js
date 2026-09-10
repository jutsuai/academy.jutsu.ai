import frappeUIPreset from 'frappe-ui/tailwind'
import { fontSize as frappeFontSize } from 'frappe-ui/tailwind/tokens.js'
import plugin from 'tailwindcss/plugin.js'
import { safeAreaPlugin } from './tailwind/safeArea.js'

// A CSS variable exposed as a Tailwind color. `color-mix` is what gives the
// `/<opacity>` modifier something to bite on — a bare `var(--x)` has no alpha
// slot, so `bg-card/60` would silently emit nothing. Same technique frappe-ui
// uses for its own semantic colors (tailwind/colorPalette.js#generateSemanticColors).
const themed = (variable) =>
	`color-mix(in srgb, var(${variable}) calc(<alpha-value> * 100%), transparent)`

// Jutsu SIEM's own token names, so markup ported from the SIEM — and any new LMS
// component that would rather say `bg-card` than `bg-surface-base` — compiles
// here too. The values resolve through styles/jutsuTokens.css, which is the one
// place either naming is defined.
const jutsuColors = {
	brand: themed('--brand'),
	'brand-foreground': themed('--brand-foreground'),
	background: themed('--background'),
	foreground: themed('--foreground'),
	card: themed('--card'),
	'card-foreground': themed('--card-foreground'),
	popover: themed('--popover'),
	'popover-foreground': themed('--popover-foreground'),
	primary: themed('--primary'),
	'primary-foreground': themed('--primary-foreground'),
	secondary: themed('--secondary'),
	'secondary-foreground': themed('--secondary-foreground'),
	muted: themed('--muted'),
	'muted-foreground': themed('--muted-foreground'),
	accent: themed('--accent'),
	'accent-foreground': themed('--accent-foreground'),
	destructive: themed('--destructive'),
	'destructive-foreground': themed('--destructive-foreground'),
	border: themed('--border'),
	input: themed('--input'),
	ring: themed('--ring'),
	'logo-plate': themed('--logo-plate'),
	sidebar: themed('--sidebar'),
	'sidebar-foreground': themed('--sidebar-foreground'),
	'sidebar-accent': themed('--sidebar-accent'),
	'sidebar-accent-foreground': themed('--sidebar-accent-foreground'),
	'sidebar-border': themed('--sidebar-border'),
	'sev-critical': themed('--sev-critical'),
	'sev-high': themed('--sev-high'),
	'sev-medium': themed('--sev-medium'),
	'sev-low': themed('--sev-low'),
	'sev-info': themed('--sev-info'),
	'status-ok': themed('--status-ok'),
	'chart-1': themed('--chart-1'),
	'chart-2': themed('--chart-2'),
	'chart-3': themed('--chart-3'),
	'chart-4': themed('--chart-4'),
	'chart-5': themed('--chart-5'),
}

// Jutsu sets no tracking on UI text; frappe-ui's Figma export carries 0.015–0.02em
// on every size, which at 14px is a visible ~0.3px of extra air per character and
// is most of what separates the two products' type colour. Rebuilt from
// frappe-ui's own token export so sizes, line-heights and weights stay in sync
// with the package — only letter-spacing changes.
//
// `tiny` is exempt: it is an uppercase eyebrow whose 0.09em IS the style.
const TRACKING_EXEMPT = new Set(['tiny', 'p-tiny'])

const fontSize = Object.fromEntries(
	Object.entries(frappeFontSize).map(([key, [size, meta]]) => [
		key,
		[size, TRACKING_EXEMPT.has(key) ? meta : { ...meta, letterSpacing: '0em' }],
	]),
)

// The weight variants (`text-base-medium`, `text-p-sm-medium`, …) are component
// classes the frappe-ui plugin registers, not utilities, so `theme.fontSize`
// above never reaches them. Re-declaring letter-spacing from a plugin of our own
// does: config plugins are resolved after preset plugins, so at equal specificity
// this wins on source order — while a real `tracking-*` utility, sitting in a
// later layer, still overrides it where a component asks for one.
const SIZES = Object.keys(frappeFontSize).filter((key) => !key.startsWith('p-'))
const WEIGHTS = ['medium', 'semibold', 'bold', 'black']

const jutsuTrackingPlugin = plugin(({ addBase, addComponents }) => {
	const components = {}
	for (const size of SIZES) {
		if (TRACKING_EXEMPT.has(size)) continue
		for (const weight of WEIGHTS) {
			components[`.text-${size}-${weight}`] = { letterSpacing: '0em' }
			components[`.text-p-${size}-${weight}`] = { letterSpacing: '0em' }
		}
	}
	addComponents(components)

	// frappe-ui's plugin pins `html` to `InterVar` and asks for Inter's own
	// variation axes (`opsz`, `cv11`). Geist has neither, and the declaration is
	// in the same layer, so it has to be restated rather than merely overridden
	// by the theme's `fontFamily.sans`.
	addBase({
		html: {
			fontFamily:
				'"Geist Variable", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
			fontOpticalSizing: 'auto',
		},
		'html, body, button, p, span, div': {
			fontVariationSettings: 'normal',
		},
	})
})

export default {
	presets: [frappeUIPreset],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
		'../node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
		'../node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
	],
	theme: {
		fontSize,
		extend: {
			colors: jutsuColors,
			fontFamily: {
				sans: [
					'Geist Variable',
					'ui-sans-serif',
					'system-ui',
					'-apple-system',
					'Segoe UI',
					'sans-serif',
				],
				mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
			},
			// Jutsu's radius ladder runs two steps past frappe's `2xl`; `4xl` is
			// what its Badge rounds with. The numbers follow the SIEM's own
			// `calc(var(--radius) * n)` formula off `--radius: 0.625rem`.
			borderRadius: {
				'3xl': '22px',
				'4xl': '26px',
			},
			// Jutsu separates cards with a border and a hairline shadow; `shadow-xs`
			// is the one it reaches for by default and frappe's scale has no `xs`.
			boxShadow: {
				xs: 'var(--elevation-sm)',
			},
			strokeWidth: {
				1.5: '1.5',
			},
			screens: {
				'2xl': '1600px',
				'3xl': '1920px',
			},
		},
	},
	plugins: [safeAreaPlugin, jutsuTrackingPlugin],
}
