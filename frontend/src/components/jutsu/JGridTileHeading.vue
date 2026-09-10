<template>
	<div class="flex items-start justify-between gap-2">
		<div v-if="$slots.leading" class="mt-0.5 shrink-0">
			<slot name="leading" />
		</div>
		<div class="min-w-0 flex-1"><slot /></div>
		<div v-if="$slots.trailing" class="shrink-0">
			<slot name="trailing" />
		</div>
	</div>
</template>

<script setup lang="ts">
/**
 * Tile title row — optional leading control (logo, checkbox), the title block,
 * and a trailing status pill. Ported from jutsu-siem
 * apps/web/src/components/soc/GridTile.tsx (`GridTileHeading`).
 */
defineSlots<{
	leading?: () => any
	default: () => any
	trailing?: () => any
}>()
</script>
