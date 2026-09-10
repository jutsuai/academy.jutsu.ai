<template>
	<component :is="tag" v-bind="linkProps" :class="wrapperClass">
		<div :class="cardClass">
			<div class="flex items-start justify-between gap-3 px-4">
				<div class="min-w-0">
					<div class="text-p-sm text-ink-gray-5">{{ label }}</div>
					<div
						:class="[
							'mt-2 text-4xl font-semibold tabular-nums leading-none xl:text-5xl',
							VALUE_CLASS[tone],
						]"
					>
						<slot name="value">{{ value }}</slot>
					</div>
				</div>
				<span
					v-if="$slots.icon"
					:class="[
						'flex size-9 shrink-0 items-center justify-center rounded-4 [&>svg]:size-4.5',
						CHIP_CLASS[colorKey],
					]"
					aria-hidden="true"
				>
					<slot name="icon" />
				</span>
			</div>
			<div v-if="hint || $slots.hint" class="px-4 pt-3 text-p-sm text-ink-gray-5">
				<slot name="hint">{{ hint }}</slot>
			</div>
		</div>
	</component>
</template>

<script setup lang="ts">
/**
 * The SIEM's KPI tile (jutsu-siem apps/web/src/components/soc/KpiCard.tsx) —
 * the control the Dashboard, Alerts and Assets pages all open with.
 *
 * Three things make it read the way it does, and all three are the point:
 *
 *   1. A tinted icon chip in the top-right — `bg-<tone>/10 text-<tone>` on a
 *      36px rounded square. It is what carries the card's semantic colour
 *      without colouring the whole card.
 *   2. A faint gradient wash rising from the bottom of the card in the same
 *      tone, at 7% — barely visible alone, but it is what stops a row of six
 *      cards reading as six identical grey boxes.
 *   3. A very large tabular-nums value, tinted by tone. `tabular-nums` matters:
 *      these numbers refresh on a live feed, and proportional digits make the
 *      whole row twitch on every poll.
 *
 * Class strings are written out per tone rather than interpolated, because
 * Tailwind only generates classes it can find whole in source.
 */
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

type Tone =
	| 'default'
	| 'brand'
	| 'critical'
	| 'high'
	| 'medium'
	| 'low'
	| 'info'
	| 'success'

/** The colour family the chip and wash resolve to (`default` borrows brand). */
type ColorKey = 'brand' | 'critical' | 'high' | 'medium' | 'low' | 'success'

const props = withDefaults(
	defineProps<{
		label: string
		value?: string | number
		hint?: string
		tone?: Tone
		/** Marks the tile as a live filter selection. */
		active?: boolean
		route?: RouteLocationRaw
	}>(),
	{ tone: 'default', active: false }
)

const VALUE_CLASS: Record<Tone, string> = {
	default: 'text-ink-gray-9',
	brand: 'text-brand',
	critical: 'text-sev-critical',
	high: 'text-sev-high',
	medium: 'text-sev-medium',
	low: 'text-sev-low',
	info: 'text-sev-info',
	success: 'text-status-ok',
}

const CHIP_CLASS: Record<ColorKey, string> = {
	brand: 'bg-brand/10 text-brand',
	critical: 'bg-sev-critical/10 text-sev-critical',
	high: 'bg-sev-high/10 text-sev-high',
	medium: 'bg-sev-medium/10 text-sev-medium',
	low: 'bg-sev-low/10 text-sev-low',
	success: 'bg-status-ok/10 text-status-ok',
}

const WASH_CLASS: Record<ColorKey, string> = {
	brand: 'from-brand/[0.07]',
	critical: 'from-sev-critical/[0.07]',
	high: 'from-sev-high/[0.07]',
	medium: 'from-sev-medium/[0.07]',
	low: 'from-sev-low/[0.07]',
	success: 'from-status-ok/[0.07]',
}

const TONE_TO_KEY: Record<Tone, ColorKey> = {
	default: 'brand',
	brand: 'brand',
	critical: 'critical',
	high: 'high',
	medium: 'medium',
	low: 'low',
	info: 'brand',
	success: 'success',
}

const colorKey = computed<ColorKey>(() => TONE_TO_KEY[props.tone])

const tag = computed(() => (props.route ? RouterLink : 'div'))
const linkProps = computed(() => (props.route ? { to: props.route } : {}))
const wrapperClass = computed(() => (props.route ? 'block h-full' : 'h-full'))

const cardClass = computed(() => [
	'relative flex h-full flex-col justify-between rounded-6 border border-outline-gray-2 py-4 shadow-xs',
	// The wash: a gradient TO the card colour, FROM the tone at 7%, rising.
	'bg-gradient-to-t to-surface-base',
	WASH_CLASS[colorKey.value],
	'transition-[border-color,box-shadow] duration-200',
	props.route ? 'hover:border-brand/30 hover:shadow-sm' : '',
	props.active ? 'border-brand/60 ring-1 ring-inset ring-brand/40' : '',
])
</script>
