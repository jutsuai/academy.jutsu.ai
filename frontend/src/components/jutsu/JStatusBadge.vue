<template>
	<span :class="['inline-flex items-center gap-1 whitespace-nowrap rounded-3 px-2 py-0.5 text-xs font-medium', TONE[tone]]">
		<slot>{{ label }}</slot>
	</span>
</template>

<script setup lang="ts">
/**
 * A workflow-state chip, ported from the SIEM's alert StatusBadge.
 *
 * Distinct from JSeverityBadge on purpose: severity is a property of the thing,
 * status is where it is in a pipeline, and the SIEM keeps them visually apart —
 * status chips are `rounded-md` with a `ring-1 ring-inset`, severity chips are
 * full pills with a border. Reusing one for the other is how a queue ends up
 * looking like it has two colour systems fighting.
 */
import { computed } from 'vue'

type Tone =
	| 'neutral'
	| 'brand'
	| 'info'
	| 'pending'
	| 'success'
	| 'warning'
	| 'danger'

const props = withDefaults(
	defineProps<{ tone?: Tone; label?: string }>(),
	{ tone: 'neutral' }
)

const TONE: Record<Tone, string> = {
	neutral: 'bg-surface-gray-2 text-ink-gray-6 ring-1 ring-inset ring-outline-gray-2',
	brand: 'bg-brand/10 text-brand ring-1 ring-inset ring-brand/25',
	info: 'bg-sev-info/10 text-sev-info ring-1 ring-inset ring-sev-info/25',
	pending: 'bg-sev-medium/10 text-sev-medium ring-1 ring-inset ring-sev-medium/25',
	success: 'bg-status-ok/10 text-status-ok ring-1 ring-inset ring-status-ok/25',
	warning: 'bg-sev-high/10 text-sev-high ring-1 ring-inset ring-sev-high/25',
	danger:
		'bg-sev-critical/10 text-sev-critical ring-1 ring-inset ring-sev-critical/25',
}

const tone = computed(() => props.tone)
</script>
