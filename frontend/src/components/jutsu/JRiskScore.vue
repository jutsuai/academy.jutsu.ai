<template>
	<div class="w-[52px]">
		<div
			:class="[
				'text-end text-base font-semibold leading-none tabular-nums',
				severityTextClass(level),
			]"
		>
			{{ score }}
		</div>
		<div class="mt-1 h-1 w-full overflow-hidden rounded-full bg-surface-gray-2">
			<div
				:class="['h-full rounded-full', severityDotClass(level)]"
				:style="{ width: `${width}%` }"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
/**
 * A 0–100 score as a tinted number over a thin proportional meter
 * (jutsu-siem apps/web/src/components/soc/RiskScore.tsx).
 *
 * The band comes from `severityFromScore`, the same function the badges use, so
 * a row cannot show a score coloured "medium" beside a chip that reads "high".
 */
import { computed } from 'vue'
import {
	severityDotClass,
	severityFromScore,
	severityTextClass,
} from '@/utils/severity'

const props = defineProps<{ score: number }>()

const level = computed(() => severityFromScore(props.score))
// Floored at 2 so a score of 0 still draws a visible sliver rather than an
// empty track that reads as "no data".
const width = computed(() => Math.max(2, Math.min(100, props.score)))
</script>
