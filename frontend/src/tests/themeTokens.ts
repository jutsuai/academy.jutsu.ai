import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import postcss from 'postcss'

// Reads the app's own theme source — src/styles/jutsuTokens.css — and resolves
// what a themed variable is actually worth under each theme.
//
// This replaced a helper that read frappe-ui's tailwind/generated/colors.json.
// That was right while frappe-ui's defaults WERE the theme; since the Jutsu port
// the app overrides those same variables in its own stylesheet, so the package's
// token data no longer describes what ships. Resolving from the stylesheet keeps
// the theme tests measuring the shipped colour rather than an upstream default
// the cascade discards.
//
// Values are oklch, so the sRGB conversion lives here too — the luma and
// contrast maths in the suites need channels, and the CSS gives none.

const ROOT = resolve(__dirname, '../..')

export type ThemeName = 'light' | 'dark'

const SELECTOR: Record<ThemeName, string> = {
	light: ':root',
	dark: "[data-theme='dark']",
}

/** Every `--*` custom property declared for `theme`, by name. */
export const themeVariables = (theme: ThemeName): Record<string, string> => {
	const css = readFileSync(resolve(ROOT, 'src/styles/jutsuTokens.css'), 'utf8')
	const out: Record<string, string> = {}
	postcss.parse(css).walkRules((rule) => {
		if (!rule.selectors.some((s) => s.trim() === SELECTOR[theme])) return
		rule.walkDecls((decl) => {
			if (decl.prop.startsWith('--')) out[decl.prop] = decl.value.trim()
		})
	})
	// Dark declares only what it changes; anything it leaves alone still holds
	// the light value, exactly as the cascade resolves it in the browser.
	if (theme === 'dark') {
		return { ...themeVariables('light'), ...out }
	}
	return out
}

/** Substitute `var(--x)` references until none are left. */
export const resolveValue = (
	value: string,
	variables: Record<string, string>
): string => {
	let out = value
	// Bounded rather than `while`: a cyclic reference in the stylesheet should
	// fail the assertion, not hang the suite.
	for (let pass = 0; pass < 8 && out.includes('var('); pass += 1) {
		out = out.replace(
			/var\((--[\w-]+)\)/g,
			(whole, name) => variables[name] ?? whole
		)
	}
	return out
}

const clamp = (value: number): number => Math.min(1, Math.max(0, value))

/** oklch(L C H) — with an optional `/ alpha`, which is dropped — to linear sRGB. */
export const oklchToLinearRgb = (value: string): [number, number, number] => {
	const match = value.match(
		/oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)(?:\s*\/[^)]*)?\)/
	)
	if (!match) throw new Error(`not an oklch colour: ${value}`)
	const lightness = match[1].endsWith('%')
		? parseFloat(match[1]) / 100
		: parseFloat(match[1])
	const chroma = parseFloat(match[2])
	const hue = (parseFloat(match[3]) * Math.PI) / 180

	const a = chroma * Math.cos(hue)
	const b = chroma * Math.sin(hue)
	const l = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
	const m = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
	const s = (lightness - 0.0894841775 * a - 1.291485548 * b) ** 3

	return [
		clamp(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
		clamp(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
		clamp(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
	]
}

/** WCAG relative luminance (0–1) of an oklch colour. */
export const relativeLuminance = (value: string): number => {
	const [r, g, b] = oklchToLinearRgb(value)
	return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/** WCAG contrast ratio between two oklch colours. */
export const contrastRatio = (a: string, b: string): number => {
	const [high, low] = [relativeLuminance(a), relativeLuminance(b)].sort(
		(x, y) => y - x
	)
	return (high + 0.05) / (low + 0.05)
}

/** `#rrggbb`, for assertions that read better as a colour than as coefficients. */
export const oklchToHex = (value: string): string => {
	const encode = (channel: number): string => {
		const srgb =
			channel <= 0.0031308
				? 12.92 * channel
				: 1.055 * channel ** (1 / 2.4) - 0.055
		return Math.round(255 * clamp(srgb))
			.toString(16)
			.padStart(2, '0')
	}
	return `#${oklchToLinearRgb(value).map(encode).join('')}`
}
