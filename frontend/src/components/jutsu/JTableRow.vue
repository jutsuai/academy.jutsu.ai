<template>
	<tr
		data-slot="table-row"
		:data-state="selected ? 'selected' : undefined"
		:class="[
			'border-b border-outline-gray-2 transition-colors last:border-0',
			selected ? 'bg-surface-gray-2' : 'hover:bg-surface-gray-2/50',
		]"
	>
		<slot />
	</tr>
</template>

<script setup lang="ts">
/**
 * A body row. Hover is a HALF-strength muted fill and selection is the full
 * one, which is what lets an open row stay visibly marked while the cursor
 * moves over its neighbours — the SIEM's queues depend on that distinction.
 */
withDefaults(defineProps<{ selected?: boolean }>(), { selected: false })
</script>
