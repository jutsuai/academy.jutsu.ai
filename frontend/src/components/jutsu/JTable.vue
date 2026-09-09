<template>
	<!-- The scroll lives on a wrapper, never on the page: a wide table must
	     scroll inside its own box or it drags the whole layout sideways. -->
	<div data-slot="table-container" class="relative w-full overflow-x-auto">
		<table data-slot="table" class="w-full caption-bottom text-base">
			<slot />
		</table>
	</div>
</template>
