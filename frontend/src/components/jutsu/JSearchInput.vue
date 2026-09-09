<template>
	<div class="relative min-w-[200px] flex-1">
		<span
			class="lucide-search pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-ink-gray-4"
			aria-hidden="true"
		/>
		<input
			:value="modelValue"
			:placeholder="placeholder"
			:aria-label="placeholder"
			type="search"
			class="h-10 w-full rounded-4 border border-outline-gray-2 bg-surface-base ps-9 pe-8 text-base text-ink-gray-9 transition-colors placeholder:text-ink-gray-4 focus-visible:border-outline-blue-4 focus-visible:outline-none"
			@input="
				emit(
					'update:modelValue',
					($event.target as HTMLInputElement).value
				)
			"
		/>
		<button
			v-if="modelValue"
			type="button"
			:aria-label="__('Clear search')"
			class="absolute end-2 top-1/2 -translate-y-1/2 rounded-1 p-0.5 text-ink-gray-4 hover:text-ink-gray-9"
			@click="emit('update:modelValue', '')"
		>
			<span class="lucide-x size-3.5 block" aria-hidden="true" />
		</button>
	</div>
</template>

<script setup lang="ts">
/**
 * The SIEM's search field (Toolbar.tsx#SearchInput): 40px tall, a leading
 * search glyph inset in the padding, and a clear button that only exists once
 * there is something to clear.
 *
 * `type="search"` rather than `text` so the control is announced as a search
 * field and phone keyboards offer a Search key.
 */
withDefaults(
	defineProps<{ modelValue: string; placeholder?: string }>(),
	{ placeholder: 'Search…' }
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
