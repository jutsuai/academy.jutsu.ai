<template>
	<div data-slot="card" :data-size="size" :class="classes">
		<slot />
	</div>
</template>

<script setup lang="ts">
/**
 * The SIEM's card (jutsu-siem apps/web/src/components/ui/card.tsx).
 *
 * A card there is a bordered `rounded-xl` surface with a hairline shadow and a
 * SINGLE spacing scale — `--card-spacing` — that the header, content and footer
 * all read, so a `size="sm"` card tightens everywhere at once instead of every
 * slot carrying its own padding. That is the part worth porting: it is why the
 * SIEM's cards look consistent at two densities and frappe's do not.
 *
 * `rounded-6` is the LMS's name for the 14px step (styles/jutsuTokens.css maps
 * it there), which is what the SIEM calls `rounded-xl`.
 */
import { computed } from 'vue'

const props = withDefaults(
	defineProps<{ size?: 'default' | 'sm' }>(),
	{ size: 'default' }
)

const classes = computed(() => [
	'group/card flex flex-col overflow-hidden rounded-6 border border-outline-gray-2 bg-surface-base text-base text-ink-gray-9 shadow-xs',
	props.size === 'sm' ? 'gap-3 py-3' : 'gap-4 py-4',
])
</script>
