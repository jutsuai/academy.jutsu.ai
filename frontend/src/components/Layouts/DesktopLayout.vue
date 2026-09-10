<template>
	<div class="flex h-dvh w-screen">
		<a
			href="#main-content"
			@click.prevent="skipToContent('main-content')"
			class="sr-only focus:not-sr-only focus:absolute focus:start-4 focus:top-4 focus:z-50 focus:rounded focus:bg-surface-base focus:px-4 focus:py-2 focus:text-ink-gray-9 focus:shadow-md focus:outline-none focus:ring-2 focus:ring-outline-gray-3"
		>
			{{ __('Skip to main content') }}
		</a>
		<!-- `jutsu-rail` (styles/jutsuChrome.css) is the SIEM's blurred sidebar
		     plane. It lives on this wrapper rather than on AppSidebar so the
		     material is declared once; AppSidebar's own root is transparent. -->
		<div class="h-full border-e jutsu-rail">
			<AppSidebar />
		</div>
		<!-- No surface of its own: the page canvas is the ruled plane painted on
		     <html> (see index.css), and cards sit on top of it. Painting
		     `bg-surface-base` here would put the card white back over the grid and
		     flatten the page/card separation the whole theme is built on. -->
		<main
			id="main-content"
			tabindex="-1"
			class="flex-1 flex flex-col h-full overflow-auto focus:outline-none"
		>
			<slot />
		</main>
	</div>
</template>
<script setup>
import { skipToContent } from '@/utils/a11y'
import AppSidebar from '@/components/Sidebar/AppSidebar.vue'
</script>
