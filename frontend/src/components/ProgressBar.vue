<template>
	<Tooltip :text="`${props.progress}%`">
		<!-- jutsu-siem apps/web/src/components/ui/progress.tsx: a `bg-muted` track
			 with a `bg-primary` indicator. The fill was `bg-surface-gray-10` —
			 frappe's solid-button grey, which resolves to near-white in dark mode.
			 Progress is the app's most-repeated "how far along" signal and the SIEM
			 paints every one of those in the brand, the same as a checked box or a
			 switch that is on. -->
		<div
			class="h-1 w-full rounded-full bg-surface-gray-2"
			:class="$attrs.class"
		>
			<div
				class="rounded-full bg-brand transition-[width] duration-300"
				:class="progressBarHeight"
				:style="{ width: progressBarWidth }"
			></div>
		</div>
	</Tooltip>
</template>

<script setup>
import { computed } from 'vue'
import { Tooltip } from 'frappe-ui'

const props = defineProps({
	progress: {
		type: Number,
		default: 0,
	},
	size: {
		type: String,
		default: 'sm',
	},
})

const progressBarWidth = computed(() => {
	const formattedPercentage = Math.min(Math.ceil(props.progress), 100)
	return `${formattedPercentage}%`
})

const progressBarHeight = computed(() => {
	if (props.size === 'sm') {
		return 'h-1'
	}
	if (props.size === 'md') {
		return 'h-2'
	}
	if (props.size === 'lg') {
		return 'h-3'
	}
})
</script>
