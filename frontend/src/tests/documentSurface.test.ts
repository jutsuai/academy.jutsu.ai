import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import postcss from 'postcss'
// The app's own theme source, so the expected colours come from the file that
// actually ships rather than from frappe-ui's defaults, which the Jutsu port
// overrides. See src/tests/themeTokens.ts.
import {
	contrastRatio,
	oklchToHex,
	relativeLuminance,
	resolveValue,
	themeVariables,
} from './themeTokens'

// The bug this guards: nothing painted the document. frappe-ui declares the
// theme variables but sets no background on html or body, and every app layout
// except MobileLayout happened to carry `bg-surface-base` on its own <main>. So
// with `data-theme="dark"` the canvas stayed the user agent's white, and on a
// phone that white filled the whole content area under near-white text.
//
// A class-name test would have passed against that bug happily — the classes in
// the markup were all real and all compiled. So this suite resolves the actual
// colour: it parses the shipped index.css for the declaration that paints the
// document, then substitutes the theme variable with the hex frappe-ui's token
// data gives it under each theme, and asserts on the result.
//
// It deliberately asserts on the *document* rather than on any component. A
// background on one more <main> would repaint that one screen and leave the
// overscroll gutter, short pages, and the next unpainted layout white.

const ROOT = resolve(__dirname, '../..')

// Walks index.css for a rule that paints the document element, and returns its
// background-color value. `html`, `:root` and `body` all paint the canvas.
const documentBackground = (): string | undefined => {
	const css = readFileSync(resolve(ROOT, 'src/index.css'), 'utf8')
	let value: string | undefined
	postcss.parse(css).walkRules((rule) => {
		const paintsDocument = rule.selectors.some((selector) =>
			['html', ':root', 'body'].includes(selector.trim())
		)
		if (!paintsDocument) return
		rule.walkDecls('background-color', (decl) => {
			value = decl.value
		})
	})
	return value
}

const documentColorScheme = (selector: string): string | undefined => {
	const css = readFileSync(resolve(ROOT, 'src/index.css'), 'utf8')
	let value: string | undefined
	postcss.parse(css).walkRules((rule) => {
		if (!rule.selectors.some((s) => s.trim() === selector)) return
		rule.walkDecls('color-scheme', (decl) => {
			value = decl.value
		})
	})
	return value
}

const resolveColour = (
	value: string,
	variables: Record<string, string>
): string => resolveValue(value, variables)

describe('the document surface follows the chosen theme', () => {
	it('paints the document from a theme variable, not a fixed colour', () => {
		const background = documentBackground()

		expect(background).toBeDefined()
		expect(background).toMatch(/^var\(--[\w-]+\)$/)
	})

	it('resolves to the near-white canvas in light mode and a near-black one in dark', () => {
		const background = documentBackground() as string

		const light = resolveColour(background, themeVariables('light'))
		const dark = resolveColour(background, themeVariables('dark'))

		// Jutsu's `--background`: a faintly cool near-white page plane that the
		// card white (`--surface-base`) sits ON, and its dark counterpart.
		expect(oklchToHex(light)).toBe('#f9fafd')
		expect(oklchToHex(dark)).toBe('#070b16')
		// Still the property that matters, independent of the exact value.
		expect(relativeLuminance(dark)).toBeLessThan(0.05)
		// The canvas has to stay distinguishable from the cards on it, or the
		// whole page flattens into one surface.
		expect(
			resolveColour('var(--surface-base)', themeVariables('dark'))
		).not.toBe(dark)
	})

	// The ink the app writes on that surface is near-white in dark mode, so a
	// white canvas put it at roughly 1.03:1 — the measured symptom.
	it('clears WCAG AA against the ink the app writes on it', () => {
		const dark = themeVariables('dark')
		const background = resolveColour(documentBackground() as string, dark)

		// The heading ink, and the secondary ink that carries most of the app's
		// body copy — the canvas has to clear AA against both, since content sits
		// directly on it wherever no card intervenes.
		expect(contrastRatio(dark['--ink-gray-9'], background)).toBeGreaterThan(4.5)
		expect(contrastRatio(dark['--ink-gray-5'], background)).toBeGreaterThan(4.5)
	})

	// Without this the browser keeps drawing scrollbars, form controls and the
	// overscroll gutter from the OS preference, which the tri-state colour mode
	// lets the user disagree with.
	it('declares a colour-scheme on both themes', () => {
		expect(documentColorScheme('html')).toBe('light')
		expect(documentColorScheme("[data-theme='dark']")).toBe('dark')
	})
})
