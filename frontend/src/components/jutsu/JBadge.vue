<template>
	<span data-slot="badge" :data-variant="variant" :class="classes">
		<slot />
	</span>
</template>

<script setup lang="ts">
/**
 * The SIEM's badge (jutsu-siem apps/web/src/components/ui/badge.tsx): a 20px
 * pill on `rounded-4xl`, 12px medium, with a tight icon slot.
 *
 * frappe-ui's Badge is close in shape but scales its type differently and has
 * no `ghost`/`link` variants; this is the SIEM's set, so a badge next to a
 * ported KPI tile matches it.
 */
import { computed } from 'vue'

type Variant =
	| 'default'
	| 'secondary'
	| 'destructive'
	| 'outline'
	| 'ghost'
	| 'link'

const props = withDefaults(defineProps<{ variant?: Variant }>(), {
	variant: 'default',
})

const VARIANT: Record<Variant, string> = {
	default: 'bg-surface-blue-6 text-ink-base',
	secondary: 'bg-surface-gray-2 text-ink-gray-6',
	destructive:
		'bg-destructive/10 text-destructive dark:bg-destructive/20',
	outline: 'border-outline-gray-2 text-ink-gray-8',
	ghost: 'text-ink-gray-6 hover:bg-surface-gray-2',
	link: 'text-brand underline-offset-4 hover:underline',
}

const classes = computed(() => [
	'inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-full border border-transparent px-2 text-xs font-medium whitespace-nowrap [&>svg]:size-3',
	VARIANT[props.variant],
])
</script>
