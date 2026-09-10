import { describe, expect, it, vi } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { mount } from '@vue/test-utils'
import postcss from 'postcss'
import {
	Button,
	Checkbox,
	FormControl,
	Popover,
	Rating,
	Select,
	Slider,
	Switch,
	TabButtons,
	Textarea,
	TextInput,
} from 'frappe-ui'

vi.stubGlobal('__', (s: string) => s)
// reka-ui's Slider measures its track on mount; jsdom has no ResizeObserver.
vi.stubGlobal(
	'ResizeObserver',
	class {
		observe() {}
		unobserve() {}
		disconnect() {}
	}
)

/**
 * styles/jutsuControls.css re-shapes every form control in the app — height,
 * fill, border, focus ring, the brand "on" state — without touching a single
 * call site. It can do that because frappe-ui stamps a semantic hook on each
 * control it renders (`data-slot`, and `data-variant` / `data-size` /
 * `data-state` from composables/useInputLabeling.ts).
 *
 * That is a contract with a dependency we do not own. If frappe-ui renames or
 * drops one of those attributes, nothing throws: every rule simply stops
 * matching, and the app quietly reverts to frappe's 28px grey slabs on the next
 * upgrade — the exact look the port exists to replace, and the kind of
 * regression that is only ever noticed by eye, weeks later.
 *
 * So this mounts the real components and asserts the hooks are on the rendered
 * DOM, then reads the stylesheet back and asserts every attribute selector it
 * relies on is one this file has proven. Adding a rule keyed on a hook nobody
 * has verified fails here rather than in production.
 */

const CSS = readFileSync(
	resolve(__dirname, '../styles/jutsuControls.css'),
	'utf8'
)

// Every `[data-*='value']` pair the stylesheet keys on, as `name=value`.
const selectorHooks = (): Set<string> => {
	const hooks = new Set<string>()
	postcss.parse(CSS).walkRules((rule) => {
		for (const [, name, value] of rule.selector.matchAll(
			/\[(data-[a-z-]+)=['"]?([a-z-]+)['"]?\]/g
		)) {
			hooks.add(`${name}=${value}`)
		}
	})
	return hooks
}

// The hooks actually present on a mounted control, same shape.
const renderedHooks = (html: string): Set<string> => {
	const hooks = new Set<string>()
	for (const [, name, value] of html.matchAll(
		/(data-(?:slot|variant|size|state|disabled|orientation))="([^"]+)"/g
	)) {
		hooks.add(`${name}=${value}`)
	}
	return hooks
}

const proven = new Set<string>()

const record = (html: string) => {
	const hooks = renderedHooks(html)
	for (const hook of hooks) proven.add(hook)
	return hooks
}

describe('the frappe-ui hooks jutsuControls.css is written against', () => {
	it('marks a text field with its slot, variant and size', () => {
		const hooks = record(mount(TextInput, { props: { size: 'sm' } }).html())

		expect(hooks).toContain('data-slot=control')
		expect(hooks).toContain('data-variant=subtle')
		expect(hooks).toContain('data-size=sm')
	})

	it('marks a textarea the same way, so one rule covers both', () => {
		const hooks = record(mount(Textarea, { props: { size: 'sm' } }).html())

		expect(hooks).toContain('data-slot=control')
		expect(hooks).toContain('data-variant=subtle')
	})

	// The outline variant is styled alongside subtle; ghost is deliberately
	// excluded (it is meant to be unfilled), which only works if the attribute
	// distinguishes them.
	it('distinguishes the variants a field can be in', () => {
		for (const variant of ['subtle', 'outline', 'ghost'] as const) {
			const hooks = record(mount(TextInput, { props: { variant } }).html())
			expect(hooks).toContain(`data-variant=${variant}`)
		}
	})

	// `data-state="invalid"` is what drives the destructive border and ring.
	it('reports an invalid field on the control itself', () => {
		const hooks = record(
			mount(TextInput, { props: { error: 'Required' } }).html()
		)

		expect(hooks).toContain('data-state=invalid')
	})

	// The one place the contract is NOT uniform, and the reason jutsuControls.css
	// matches triggers on their slot rather than their variant. Select builds its
	// own trigger and forwards neither `data-variant` nor `data-size`; Combobox
	// and MultiSelect (via the shared selection trigger) forward both. A rule
	// keyed on the variant therefore skipped every <Select> in the app —
	// invisibly, since the control still rendered, just in frappe's shape.
	it('marks a select trigger by slot, but stamps no variant or size on it', () => {
		const hooks = record(
			mount(Select, {
				props: { size: 'sm', options: [{ label: 'One', value: '1' }] },
			}).html()
		)

		expect(hooks).toContain('data-slot=trigger')
		expect(hooks).not.toContain('data-variant=subtle')
		expect(hooks).not.toContain('data-size=sm')
	})

	// So the height falls back to the size class Select does render, and the
	// ghost exclusion falls back to the fill class. Both are pinned here because
	// a stylesheet keyed on a class is only as good as the class surviving.
	it('renders the size and fill classes those trigger rules fall back to', () => {
		const trigger = mount(Select, {
			props: { size: 'sm', options: [{ label: 'One', value: '1' }] },
		}).get('[data-slot="trigger"]')

		expect(trigger.classes()).toContain('min-h-7')
		expect(trigger.classes()).toContain('bg-surface-gray-2')
		expect(trigger.classes()).not.toContain('bg-transparent')

		const ghost = mount(Select, {
			props: { variant: 'ghost', options: [{ label: 'One', value: '1' }] },
		}).get('[data-slot="trigger"]')

		expect(ghost.classes()).toContain('bg-transparent')
	})

	// `data-disabled` is what the muted disabled fill keys on.
	it('marks a disabled control as disabled', () => {
		const hooks = record(mount(TextInput, { props: { disabled: true } }).html())

		expect(hooks).toContain('data-disabled=true')
	})

	// The binary controls carry `data-slot="control"` too — which is exactly why
	// the height rule has to exclude them, or a checkbox comes out 32px tall.
	// That regression happened once already.
	it('marks a checkbox as a control, and as a checkbox', () => {
		const wrapper = mount(Checkbox, { props: { label: 'Featured' } })
		record(wrapper.html())
		const input = wrapper.get('[data-slot="control"]')

		expect(input.attributes('type')).toBe('checkbox')
	})

	it('gives a switch the role the brand fill is keyed on', () => {
		const wrapper = mount(Switch, { props: { modelValue: true } })
		const control = wrapper.get('[role="switch"]')

		expect(control.attributes('data-state')).toBe('checked')
		proven.add('data-state=checked')
	})

	it('marks each tab button, so the segmented track can be measured', () => {
		const wrapper = mount(TabButtons, {
			props: {
				modelValue: 'a',
				options: [
					{ label: 'A', value: 'a' },
					{ label: 'B', value: 'b' },
				],
			},
		})
		record(wrapper.html())

		expect(wrapper.findAll('[data-slot="tab-button"]').length).toBe(2)
	})

	// FormControl is what most of the LMS actually calls; it delegates, and the
	// delegation is the part that could silently change.
	it('passes the hooks through FormControl, which most pages use', () => {
		const hooks = record(
			mount(FormControl, { props: { type: 'text', size: 'sm' } }).html()
		)

		expect(hooks).toContain('data-slot=control')
		expect(hooks).toContain('data-variant=subtle')
	})

	// The backstop: a rule keyed on a hook no test above has seen on real markup
	// is a rule that may already be dead.
	it('keys every rule on a hook that a real control emits', () => {
		const unproven = [...selectorHooks()].filter((hook) => !proven.has(hook))

		expect(unproven).toEqual([])
	})
})

/**
 * The other half of the contract, and the one that actually bit.
 *
 * `data-slot="control"` does not mean "text field" — frappe-ui puts it on every
 * control it labels. A draft of jutsuControls.css keyed its height rule on
 * `[data-slot='control'][data-size='sm']`, which also matched the Switch's
 * <button> root: every toggle in the app became a 26x32 blob, on every page,
 * from one line of CSS. Nothing failed; it just looked wrong.
 *
 * So rather than trusting the selectors by reading them, this runs them. Each
 * component that carries the slot is mounted for real, every field rule in the
 * stylesheet is applied to its DOM with `matches()`, and the ones that are not
 * text fields must match none of them.
 */

// Field rules only — the checkbox, switch and tab-button sections deliberately
// DO target those controls. `:has()` is skipped: jsdom's selector engine does
// not implement it, and the one rule using it is scoped to a tab strip anyway.
const fieldSelectors = (): string[] => {
	const out: string[] = []
	postcss.parse(CSS).walkRules((rule) => {
		for (const selector of rule.selectors) {
			if (selector.includes(':has(')) continue
			if (
				!selector.includes("[data-slot='control']") &&
				!selector.includes("[data-slot='trigger']")
			)
				continue
			if (/\[type='(checkbox|radio)'\]\[data-slot/.test(selector)) continue
			// Drop the interaction pseudo-classes: jsdom cannot put an element
			// into :hover or :focus-visible, and what is under test is which
			// ELEMENTS a rule reaches, not when it fires.
			out.push(
				selector
					.replace(/:hover|:focus-visible|:focus-within|:disabled/g, '')
					.trim()
			)
		}
	})
	return [...new Set(out)]
}

const matchedBy = (root: Element): string[] =>
	fieldSelectors().filter((selector) => {
		const all = [root, ...Array.from(root.querySelectorAll('*'))]
		return all.some((el) => {
			try {
				return el.matches(selector)
			} catch {
				return false
			}
		})
	})

describe('what the field rules in jutsuControls.css actually reach', () => {
	it('reaches a text input and a textarea', () => {
		expect(matchedBy(mount(TextInput).element as Element).length).toBeGreaterThan(0)
		expect(matchedBy(mount(Textarea).element as Element).length).toBeGreaterThan(0)
	})

	// The regression. A switch is a pill, and nothing in the field section may
	// touch its height, its fill or its border.
	it('leaves a switch alone', () => {
		expect(matchedBy(mount(Switch).element as Element)).toEqual([])
	})

	// The other roots that carry the slot. CodeEditor is not among them here —
	// frappe-ui exports it as a lazily-resolved component that test-utils cannot
	// mount directly — but it is a plain <div class="code-editor">, so the
	// element-scoped selectors above cannot reach it either.
	it('leaves a slider and a rating alone', () => {
		expect(matchedBy(mount(Slider).element as Element)).toEqual([])
		expect(matchedBy(mount(Rating).element as Element)).toEqual([])
	})

	// A checkbox is sized by its own block; the field rules must not also claim
	// it, or it comes out 32px tall.
	it('leaves a checkbox alone', () => {
		expect(matchedBy(mount(Checkbox).element as Element)).toEqual([])
	})

	// The same trap one level along: Popover stamps `data-slot="trigger"` too,
	// but as-child — so it lands on whatever the caller passed, which in this app
	// is nearly always a plain <Button>. A rule keyed on the bare slot would give
	// every popover trigger a field's fill, border and focus ring.
	it('leaves a popover trigger alone', () => {
		const wrapper = mount(Popover, {
			slots: {
				trigger: '<button type="button" class="bg-surface-gray-2">Open</button>',
				default: '<div>panel</div>',
			},
		})

		expect(wrapper.find('[data-slot="trigger"]').exists()).toBe(true)
		expect(matchedBy(wrapper.element as Element)).toEqual([])
	})

	// And a Select trigger, which carries neither variant nor size, still must be
	// reached — that is the whole reason the combobox-role half of the selector
	// exists.
	it('still reaches a select trigger', () => {
		const wrapper = mount(Select, {
			props: { size: 'sm', options: [{ label: 'One', value: '1' }] },
		})

		expect(matchedBy(wrapper.element as Element).length).toBeGreaterThan(0)
	})
})
