<template>
	<span
		:class="[
			'inline-flex h-5 w-fit shrink-0 items-center gap-1 whitespace-nowrap rounded-full border px-2 text-xs font-medium capitalize',
			severityBadgeClass(level),
		]"
	>
		<span
			v-if="dot"
			:class="['size-1.5 rounded-full', severityDotClass(level)]"
			aria-hidden="true"
		/>
		<slot>{{ normalizeSeverity(level) }}</slot>
	</span>
</template>

<script setup lang="ts">
/**
 * Severity as the SIEM renders it: a tinted pill at 12% fill with matching
 * text and a 30% border. Levels and class maps come from utils/severity.ts, so
 * a badge, a risk meter and a chart bar for the same level cannot disagree.
 */
import {
	normalizeSeverity,
	severityBadgeClass,
	severityDotClass,
} from '@/utils/severity'

withDefaults(defineProps<{ level?: string; dot?: boolean }>(), { dot: false })
</script>
