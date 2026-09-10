<template>
	<!-- The SIEM's footer is a tinted band flush with the card's bottom edge:
	     it cancels the card's own bottom padding and paints `bg-muted/50`. -->
	<div
		data-slot="card-footer"
		class="-mb-4 flex items-center gap-2 border-t border-outline-gray-2 bg-surface-gray-2/50 px-4 py-3 group-data-[size=sm]/card:-mb-3 group-data-[size=sm]/card:px-3"
	>
		<slot />
	</div>
</template>
