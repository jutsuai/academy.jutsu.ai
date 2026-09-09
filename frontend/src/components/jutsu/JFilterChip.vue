<template>
	<button
		type="button"
		:aria-pressed="active"
		:class="[
			'inline-flex h-7 items-center gap-1.5 rounded-full border px-3 text-xs font-medium transition-colors',
			active
				? 'border-brand/50 bg-brand/15 text-ink-gray-9'
				: 'border-outline-gray-2 bg-transparent text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-9',
		]"
	>
		<span
			v-if="dot"
			:class="['size-1.5 rounded-full', severityDotClass(dot)]"
			aria-hidden="true"
		/>
		<slot>{{ label }}</slot>
		<span
			v-if="typeof count === 'number'"
			:class="['tabular-nums', active ? 'text-ink-gray-8' : 'text-ink-gray-4']"
		>
			{{ count }}
		</span>
	</button>
</template>

<script setup lang="ts">
/**
 * The count chip from the SIEM's queue toolbars — "Resolved 71", "Escalated 38".
 * Ported from apps/web/src/components/soc/Toolbar.tsx#FilterChip.
 *
 * The count is a separate, dimmer span rather than part of the label, and it is
 * `tabular-nums`: these refresh live, and proportional digits make a whole row
 * of chips resize on every poll.
 */
import { severityDotClass } from '@/utils/severity'

withDefaults(
	defineProps<{
		label?: string
		active?: boolean
		count?: number
		/** A severity key, for the leading dot. */
		dot?: string
	}>(),
	{ active: false }
)
</script>
