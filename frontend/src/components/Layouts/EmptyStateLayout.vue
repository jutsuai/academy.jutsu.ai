<template>
	<div class="relative flex h-full min-h-64 w-full grow justify-center">
		<!-- jutsu-siem apps/web/src/components/ui/empty.tsx, as the Sigma
			 marketplace uses it: a dashed panel over the canvas rather than a
			 loose column of text, with the icon in an `EmptyMedia variant="icon"`
			 tile (size-8, rounded, muted fill). On a ruled canvas a bare centred
			 paragraph reads as a page that failed to render; a dashed outline
			 reads as a container that is deliberately empty. -->
		<div
			class="absolute inset-x-0 top-1/4 mx-auto flex w-full flex-col items-center gap-4 rounded-md border border-dashed border-outline-gray-2 bg-surface-base/50 p-6 text-center sm:top-[30%]"
			:class="widthClass"
		>
			<span
				class="grid size-8 shrink-0 place-items-center rounded-4 bg-surface-gray-2 text-ink-gray-7"
			>
				<span class="size-4" :class="icon" />
			</span>
			<div class="flex flex-col items-center gap-1">
				<span
					class="text-base-medium text-center text-ink-gray-8 sm:text-lg-medium"
				>
					{{ computedTitle }}
				</span>
				<span class="text-center text-p-sm text-ink-gray-6 sm:text-p-base">
					{{ computedDescription }}
				</span>
			</div>
			<slot />
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
	defineProps<{
		name: string
		title?: string
		description?: string
		icon?: string
		width?: 'sm' | 'md' | 'lg'
	}>(),
	{
		icon: 'lucide-graduation-cap',
		width: 'md',
	}
)

const computedTitle = computed(
	() => props.title || __('No {0} Found').format(props.name)
)

const computedDescription = computed(
	() =>
		props.description ||
		__(
			'There are no {0} currently. Keep an eye out, fresh learning experiences are on the way!'
		).format(props.name?.toLowerCase())
)

// The fractional widths are desktop-only. Unqualified, `w-4/12` is about 130px
// on a 390px phone, which wrapped the copy into a sliver a word or two wide.
// The base `w-full` holds until `sm`, and these take over from there.
//
// Centring is `inset-x-0 mx-auto` rather than the half-offset-and-translate
// pair it replaced: same result, no physical inline-axis class for the RTL
// rule to catch.
const widthClass = computed(() => {
	switch (props.width) {
		case 'sm':
			return 'sm:w-2/12'
		case 'lg':
			return 'sm:w-8/12'
		default:
			return 'sm:w-4/12'
	}
})
</script>
