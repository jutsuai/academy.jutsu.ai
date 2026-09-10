<template>
	<component
		:is="tag"
		:type="tag === 'button' ? 'button' : undefined"
		:data-row-id="rowId || undefined"
		:data-state="selected ? 'selected' : undefined"
		:aria-disabled="disabled || undefined"
		:disabled="tag === 'button' && disabled ? true : undefined"
		:tabindex="tag !== 'button' && interactive ? 0 : undefined"
		:class="classes"
		@click="onActivate"
		@keydown="onKeydown"
	>
		<slot />
	</component>
</template>

<script setup lang="ts">
/**
 * The SIEM's results-grid tile, ported from jutsu-siem
 * apps/web/src/components/soc/GridTile.tsx.
 *
 * This is the card the Assets and Alerts grids are built from, and it is a
 * different object from the LMS's catalogue card: dense (px-3 py-2.5, gap-2.5),
 * small type, and a footer of chips pinned with `mt-auto` so every tile in a
 * grid row shares one baseline no matter how long its title ran.
 *
 * The fill is the tile's one subtle move. A tile sits inside a card, so `bg-card`
 * would be the exact colour of the surface behind it; instead the card colour is
 * mixed 4.5% toward the foreground, which lifts it by the same *gesture* in both
 * themes (lighter on the dark canvas, darker on the light one) rather than by a
 * hard-coded pair of colours.
 */
import { computed, useAttrs } from 'vue'

defineOptions({ inheritAttrs: true })

const props = withDefaults(
	defineProps<{
		selected?: boolean
		disabled?: boolean
		/** The record this tile stands for, so a `?id=` deep link can find it. */
		rowId?: string
		/** Native button when the tile has no nested interactive children. */
		as?: 'div' | 'button'
	}>(),
	{ as: 'div' }
)

const emit = defineEmits<{ activate: [] }>()

const attrs = useAttrs()

// A tile is only interactive when something is listening. `onClick` in the SIEM;
// here the parent either listens for `activate` or wraps the tile in a link.
const interactive = computed(
	() => Boolean(attrs.onActivate) && !props.disabled
)

const tag = computed(() => props.as)

const TILE = [
	'group relative flex h-full min-h-0 w-full flex-col gap-2.5 rounded-4 border px-3 py-2.5 text-left',
	'border-outline-gray-2 bg-[color-mix(in_oklab,var(--foreground)_4.5%,var(--surface-base))]',
	'transition-[border-color,background-color] duration-150',
	'hover:border-brand/40 hover:bg-[color-mix(in_oklab,var(--foreground)_9%,var(--surface-base))]',
	'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40',
].join(' ')

const classes = computed(() => [
	TILE,
	props.selected ? 'border-brand/50 bg-brand/[0.08] hover:border-brand/50' : '',
	props.disabled ? 'opacity-40' : '',
	interactive.value ? 'cursor-pointer' : '',
])

const onActivate = () => {
	if (interactive.value) emit('activate')
}

// Enter/Space on the tile itself, never on a control inside it — a menu button
// in the footer handles its own keys and must not also open the tile.
const onKeydown = (event: KeyboardEvent) => {
	if (event.defaultPrevented || !interactive.value) return
	if (event.target !== event.currentTarget) return
	if (event.key === 'Enter' || event.key === ' ') {
		event.preventDefault()
		emit('activate')
	}
}
</script>
