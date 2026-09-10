<template>
	<td
		data-slot="table-cell"
		:class="[
			'px-3 py-2.5 align-middle',
			numeric ? 'text-end tabular-nums' : '',
			mono ? 'font-mono text-[13px]' : '',
			wrap ? '' : 'whitespace-nowrap',
		]"
	>
		<slot />
	</td>
</template>

<script setup lang="ts">
/**
 * `mono` sets machine values — IPs, hostnames, technique IDs — in the mono
 * face, and `numeric` right-aligns with tabular figures so a column of counts
 * lines up on the digit. Both are how the SIEM's tables stay scannable.
 */
withDefaults(
	defineProps<{ numeric?: boolean; mono?: boolean; wrap?: boolean }>(),
	{ numeric: false, mono: false, wrap: false }
)
</script>
