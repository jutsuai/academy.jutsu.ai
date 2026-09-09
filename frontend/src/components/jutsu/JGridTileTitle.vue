<template>
	<span
		class="line-clamp-2 text-p-base-medium leading-snug text-ink-gray-9"
	>
		<slot />
	</span>
</template>

<script setup lang="ts">
/**
 * `GridTileTitle` from jutsu-siem apps/web/src/components/soc/GridTile.tsx:
 * `text-sm font-medium`, clamped at two lines. Deliberately small — a tile in
 * the SIEM's grid is a data row that happens to be laid out as a card, not a
 * poster.
 */
</script>
