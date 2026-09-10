<template>
	<div
		class="inline-flex items-center rounded-3 border border-outline-gray-2 bg-surface-base/50 p-0.5"
		role="group"
	>
		<button
			v-for="option in options"
			:key="option.value"
			type="button"
			:aria-pressed="modelValue === option.value"
			:aria-label="option.label"
			:title="option.label"
			:class="[
				'inline-flex h-7 items-center gap-1.5 rounded-2 px-2.5 text-xs font-medium transition-colors',
				modelValue === option.value
					? 'bg-surface-gray-2 text-ink-gray-9 shadow-xs'
					: 'text-ink-gray-5 hover:text-ink-gray-9',
			]"
			@click="emit('update:modelValue', option.value)"
		>
			<component
				:is="option.icon"
				v-if="option.icon"
				class="size-4"
				aria-hidden="true"
			/>
			<span v-if="!iconOnly">{{ option.label }}</span>
		</button>
	</div>
</template>

<script setup lang="ts">
/**
 * The SIEM's segmented control (Toolbar.tsx#Segmented, and the grid/list
 * LayoutToggle, which is the same control with `iconOnly`).
 *
 * The selected segment is a raised `bg-secondary shadow-xs` chip inside a
 * bordered tray — not a brand fill. That distinction is deliberate in the SIEM:
 * brand marks *what you are looking at* (the active nav item, an applied
 * filter), while a segmented control only changes how the same data is drawn,
 * so it stays neutral.
 */
import type { Component } from 'vue'

defineProps<{
	options: { value: string; label: string; icon?: Component }[]
	modelValue: string
	iconOnly?: boolean
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
