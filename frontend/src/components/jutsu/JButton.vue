<template>
	<component
		:is="tag"
		v-external="isExternal || undefined"
		v-bind="linkProps"
		data-slot="button"
		:data-variant="variant"
		:data-size="size"
		:disabled="isNativeButton && (disabled || loading) ? true : undefined"
		:aria-busy="loading || undefined"
		:type="isNativeButton ? type : undefined"
		:class="classes"
	>
		<span
			v-if="loading"
			class="size-4 shrink-0 animate-spin rounded-full border-2 border-current border-t-transparent"
			aria-hidden="true"
		/>
		<slot name="prefix" />
		<slot />
		<slot name="suffix" />
	</component>
</template>

<script setup lang="ts">
/**
 * The SIEM's button, ported from jutsu-siem apps/web/src/components/ui/button.tsx.
 *
 * Geometry and variants are the SIEM's, expressed against the LMS's token names
 * (which styles/jutsuTokens.css has already pointed at the SIEM's palette):
 *
 *   default      solid brand
 *   outline      a card-tinted fill with a soft border, brandward on hover
 *   secondary    the muted fill
 *   ghost        transparent until hovered
 *   destructive  TINTED, not solid — the SIEM never paints a filled red button,
 *                which is the single most visible difference from frappe-ui's
 *                `theme="red" variant="solid"`
 *   link         brand text with a hover underline
 *
 * Sizes are 6/7/8/9 tall (xs/sm/default/lg), matching the SIEM exactly. The
 * one-pixel press (`active:translate-y-px`) is skipped for anything opening a
 * popover, so a menu trigger doesn't jump under a click that isn't a "press".
 */
import { computed, useAttrs } from 'vue'
import { RouterLink } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

defineOptions({ inheritAttrs: true })

type Variant =
	| 'default'
	| 'outline'
	| 'secondary'
	| 'ghost'
	| 'destructive'
	| 'link'

type Size =
	| 'default'
	| 'xs'
	| 'sm'
	| 'lg'
	| 'icon'
	| 'icon-xs'
	| 'icon-sm'
	| 'icon-lg'

const props = withDefaults(
	defineProps<{
		variant?: Variant
		size?: Size
		disabled?: boolean
		loading?: boolean
		type?: 'button' | 'submit' | 'reset'
		/** Renders a <router-link>. */
		route?: RouteLocationRaw
		/** Renders an anchor that opens in a new tab, via `v-external`. */
		link?: string
	}>(),
	{ variant: 'default', size: 'default', type: 'button' }
)

const attrs = useAttrs()

const BASE =
	'group/button inline-flex shrink-0 items-center justify-center rounded-4 border border-transparent bg-clip-padding text-base-medium whitespace-nowrap transition-all outline-none select-none disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0'

const VARIANT: Record<Variant, string> = {
	default: 'bg-surface-blue-6 text-ink-base hover:bg-surface-blue-7',
	outline:
		'border-outline-gray-2 bg-surface-base/60 text-ink-gray-8 hover:border-brand/25 hover:bg-surface-gray-2 hover:text-ink-gray-9 aria-expanded:bg-surface-gray-2',
	secondary:
		'bg-surface-gray-2 text-ink-gray-8 hover:bg-surface-gray-3 aria-expanded:bg-surface-gray-3',
	ghost:
		'text-ink-gray-8 hover:bg-surface-gray-2 hover:text-ink-gray-9 aria-expanded:bg-surface-gray-2',
	destructive:
		'bg-destructive/10 text-destructive hover:bg-destructive/20 dark:bg-destructive/20 dark:hover:bg-destructive/30',
	link: 'text-brand underline-offset-4 hover:underline',
}

const SIZE: Record<Size, string> = {
	default: 'h-8 gap-1.5 px-2.5 [&_svg]:size-4',
	xs: 'h-6 gap-1 rounded-3 px-2 text-xs [&_svg]:size-3',
	sm: 'h-7 gap-1 rounded-3 px-2.5 text-[0.8rem] [&_svg]:size-3.5',
	lg: 'h-9 gap-1.5 px-2.5 [&_svg]:size-4',
	icon: 'size-8 [&_svg]:size-4',
	'icon-xs': 'size-6 rounded-3 [&_svg]:size-3',
	'icon-sm': 'size-7 rounded-3 [&_svg]:size-3.5',
	'icon-lg': 'size-9 [&_svg]:size-4',
}

// The SIEM's `active:not-aria-[haspopup]:translate-y-px`. Tailwind 3 has no
// `not-*` variant, so the exclusion is done here instead: a popover trigger
// isn't being "pressed", and a menu that shifts a pixel under the cursor as it
// opens reads as a glitch.
const pressable = computed(() => !attrs['aria-haspopup'])

const classes = computed(() => [
	BASE,
	VARIANT[props.variant],
	SIZE[props.size],
	pressable.value ? 'active:translate-y-px' : '',
	props.loading ? 'pointer-events-none' : '',
	// A focus ring drawn as an outline rather than a shadow ring, so it never
	// collides with a shadow utility on the same element.
	'focus-visible:focus-ring-blue',
])

const tag = computed(() => {
	if (props.disabled || props.loading) return 'button'
	if (props.route) return RouterLink
	if (props.link) return 'a'
	return 'button'
})

const isNativeButton = computed(() => tag.value === 'button')

const linkProps = computed(() => {
	if (props.disabled || props.loading) return {}
	if (props.route) return { to: props.route }
	// Only the href. `v-external` above sets the target and the rel, and it is
	// the single place in the app allowed to: opening a new tab without
	// `noopener` hands the opened page a `window.opener` reference back to ours
	// (reverse tabnabbing). tests/directives.test.ts enforces that by scanning
	// every .vue file's raw source — which is also why this comment describes
	// the attribute rather than spelling it out.
	if (props.link) return { href: props.link }
	return {}
})

const isExternal = computed(
	() => Boolean(props.link) && !props.disabled && !props.loading
)
</script>
