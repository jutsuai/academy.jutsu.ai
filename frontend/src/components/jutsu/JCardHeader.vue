<template>
	<div data-slot="card-header" :class="classes">
		<div class="grid min-w-0 auto-rows-min items-start gap-1">
			<div
				v-if="title || $slots.title"
				data-slot="card-title"
				class="text-lg-medium leading-snug text-ink-gray-9"
			>
				<slot name="title">{{ title }}</slot>
			</div>
			<div
				v-if="description || $slots.description"
				data-slot="card-description"
				class="text-p-sm text-ink-gray-5"
			>
				<slot name="description">{{ description }}</slot>
			</div>
		</div>
		<div
			v-if="$slots.actions"
			data-slot="card-action"
			class="shrink-0 self-start"
		>
			<slot name="actions" />
		</div>
	</div>
</template>

<script setup lang="ts">
/**
 * Card header: title over an optional description, with actions pinned to the
 * trailing edge. The SIEM builds this with a CSS grid whose second column only
 * exists when a `card-action` is present; a flex row with a `shrink-0` action
 * is the same result with far less machinery, and Vue can just ask whether the
 * slot was passed.
 */
import { computed } from 'vue'

const props = withDefaults(
	defineProps<{
		title?: string
		description?: string
		/** Draws the divider the SIEM's `[.border-b]` header variant carries. */
		bordered?: boolean
	}>(),
	{ bordered: false }
)

const classes = computed(() => [
	'flex items-start justify-between gap-3 px-4 group-data-[size=sm]/card:px-3',
	props.bordered ? 'border-b border-outline-gray-2 pb-4' : '',
])
</script>
