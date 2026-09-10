<template>
	<span
		class="inline-flex h-5 items-center rounded-2 bg-surface-gray-2 px-1.5 font-mono text-[11px] leading-none text-ink-gray-5"
	>
		<slot />
	</span>
</template>

<script setup lang="ts">
/**
 * The monospace source chip from the SIEM's asset cards — `linux.auth`,
 * `windows.sysmon`, `gws.login`.
 *
 * Monospace on purpose: these are machine identifiers, and setting them in the
 * UI face makes them read as prose. It is the same reason the SIEM sets IPs and
 * MITRE technique IDs in mono in its tables.
 */
</script>
