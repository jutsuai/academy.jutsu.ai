<template>
	<div class="relative flex h-full flex-col">
		<a
			href="#scrollContainer"
			@click.prevent="skipToContent('scrollContainer')"
			class="sr-only focus:not-sr-only focus:absolute focus:start-4 focus:top-4 focus:z-50 focus:rounded focus:bg-surface-base focus:px-4 focus:py-2 focus:text-ink-gray-9 focus:shadow-md focus:outline-none focus:ring-2 focus:ring-outline-gray-3"
		>
			{{ __('Skip to main content') }}
		</a>
		<div class="h-full flex-1">
			<!-- No surface of its own. This layout was deliberately left opaque when
			     the theme first landed, on the reasoning that a long-form reader
			     wants a calm sheet rather than a ruled plane — the SIEM does exactly
			     that for its compliance pages. In this product the opposite reads
			     better: the lesson view sits beside the course editor, which is on
			     the canvas, and the two looked like different applications. -->
			<div class="flex h-dvh text-base">
				<main
					class="w-full overflow-auto focus:outline-none"
					id="scrollContainer"
					tabindex="-1"
				>
					<slot />
				</main>
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { skipToContent } from '@/utils/a11y'
</script>
