<template>
	<th
		data-slot="table-head"
		:class="[
			'h-10 px-3 text-start align-middle text-p-sm font-medium whitespace-nowrap text-ink-gray-5',
			sortable ? 'cursor-pointer select-none hover:text-ink-gray-9' : '',
			numeric ? 'text-end tabular-nums' : '',
		]"
		:aria-sort="ariaSort"
	>
		<span class="inline-flex items-center gap-1">
			<slot />
			<span
				v-if="sortable"
				class="lucide-chevrons-up-down size-3 text-ink-gray-4"
				aria-hidden="true"
			/>
		</span>
	</th>
</template>

<script setup lang="ts">
/**
 * A column header on the SIEM's 40px header row: muted, medium, never wrapping,
 * with the sort affordance shown as a chevron pair beside the label.
 *
 * `aria-sort` is derived rather than left to the caller — a sortable column
 * that never announces its direction is invisible to a screen reader, and this
 * is the one place that can be enforced for every table at once.
 */
import { computed } from 'vue'

const props = withDefaults(
	defineProps<{
		sortable?: boolean
		numeric?: boolean
		direction?: 'asc' | 'desc' | null
	}>(),
	{ sortable: false, numeric: false, direction: null }
)

const ariaSort = computed(() => {
	if (!props.sortable) return undefined
	if (props.direction === 'asc') return 'ascending'
	if (props.direction === 'desc') return 'descending'
	return 'none'
})
</script>
