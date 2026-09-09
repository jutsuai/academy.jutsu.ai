import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.stubGlobal('__', (text: string) => text)
// translation.js installs String.prototype.format at app boot; the component
// calls __('No {0} Found').format(name) and never reaches Vue without it.
if (!('format' in String.prototype)) {
	// eslint-disable-next-line no-extend-native
	Object.defineProperty(String.prototype, 'format', {
		value: function (...args: string[]) {
			return this.replace(/\{(\d+)\}/g, (_: string, i: number) => args[i] ?? '')
		},
	})
}

import EmptyStateLayout from '@/components/Layouts/EmptyStateLayout.vue'

// The class strings ARE the behaviour here — this component renders nothing but
// layout, and the bug being fixed was a width that had no mobile treatment at
// all. Each assertion below fails if its class is removed; there is no
// behavioural proxy to assert instead.
const mountEmpty = (props: Record<string, unknown> = {}) =>
	mount(EmptyStateLayout, {
		props: { name: 'Courses', ...props },
		global: { mocks: {}, stubs: {} },
	})

describe('EmptyStateLayout', () => {
	it('fills the phone width, and only narrows from sm up', () => {
		const panel = mountEmpty().get('[class*="absolute"]')

		expect(panel.classes()).toContain('w-full')
		expect(panel.classes()).toContain('sm:w-4/12')
		// The unqualified fractional width was the bug: ~130px on a 390px screen.
		expect(panel.classes()).not.toContain('w-4/12')
	})

	it('keeps the desktop widths behind sm for every size', () => {
		expect(
			mountEmpty({ width: 'sm' }).get('[class*="absolute"]').classes()
		).toContain('sm:w-2/12')
		expect(
			mountEmpty({ width: 'lg' }).get('[class*="absolute"]').classes()
		).toContain('sm:w-8/12')
	})

	// The icon used to be a loose 40px glyph that shrank to 30px on the desk.
	// It is now the SIEM's `EmptyMedia variant="icon"` (ui/empty.tsx): one
	// fixed 32px tile with a muted fill and a 16px glyph inside it, at every
	// width. The glyph no longer carries the size — the tile does — so a
	// stray `size-*` back on the glyph would silently break the tile's
	// centring, which is what this pins.
	it('sets the icon in a tile rather than sizing the glyph itself', () => {
		const glyph = mountEmpty().get('span.lucide-graduation-cap')
		const tile = glyph.element.parentElement as HTMLElement

		expect(glyph.classes()).toContain('size-4')
		expect(tile.className).toContain('size-8')
		expect(tile.className).toContain('place-items-center')
		expect(tile.className).toContain('bg-surface-gray-2')
	})

	// On the ruled canvas a bare centred paragraph reads as a page that failed
	// to render. The SIEM outlines an empty region instead (ui/empty.tsx, as
	// the Sigma marketplace uses it: `border border-dashed border-border/60
	// bg-card/50`), so the emptiness is visibly a container and not a gap.
	it('outlines the empty region rather than leaving it bare', () => {
		const panel = mountEmpty().get('[class*="absolute"]')

		expect(panel.classes()).toContain('border')
		expect(panel.classes()).toContain('border-dashed')
	})

	it('steps the type down on a phone rather than up', () => {
		const wrapper = mountEmpty()
		const title = wrapper.get('.text-base-medium')
		const description = wrapper.get('.text-p-sm')

		expect(title.classes()).toContain('sm:text-lg-medium')
		expect(description.classes()).toContain('sm:text-p-base')
	})

	it('centres without a physical offset, so RTL is unaffected', () => {
		const panel = mountEmpty().get('[class*="absolute"]')

		expect(panel.classes()).toContain('inset-x-0')
		expect(panel.classes()).toContain('mx-auto')
		expect(panel.classes()).not.toContain('left-1/2')
	})

	it('still renders the copy it is given', () => {
		const wrapper = mountEmpty({
			title: 'Nothing here',
			description: 'Try again later',
		})

		expect(wrapper.text()).toContain('Nothing here')
		expect(wrapper.text()).toContain('Try again later')
	})
})
