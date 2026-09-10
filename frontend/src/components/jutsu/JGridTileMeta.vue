<template>
	<div
		class="mt-auto flex flex-wrap items-center gap-1.5 border-t border-outline-gray-1 pt-2"
	>
		<slot />
		<span
			v-if="$slots.end"
			class="ms-auto inline-flex shrink-0 items-center gap-1 text-p-xs tabular-nums text-ink-gray-5"
		>
			<slot name="end" />
		</span>
	</div>
</template>

<script setup lang="ts">
/**
 * The tile's footer row, from jutsu-siem apps/web/src/components/soc/GridTile.tsx
 * (`GridTileMeta`). `mt-auto` is what makes a grid of tiles share one baseline:
 * the footer is pushed to the bottom of whatever height the row settled on, so
 * a two-line title and a one-line title still line up along the rule.
 */
defineSlots<{ default?: () => any; end?: () => any }>()
</script>
