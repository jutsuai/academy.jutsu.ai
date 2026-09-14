<template>
	<button
		v-if="link && !link.onlyMobile"
		:data-notifications-trigger="link.panel === 'notifications' ? '' : null"
		:data-active="isActive"
		class="jutsu-nav-item flex cursor-pointer items-center rounded-4 text-ink-gray-8 transition-colors duration-200 ease-out focus:outline-none focus-visible:focus-ring-blue"
		:class="[
			isCollapsed ? 'mx-auto w-11' : 'w-full',
			isActive
				? 'bg-brand/10 font-medium text-brand ring-1 ring-inset ring-brand/20 hover:bg-brand/[0.15]'
				: 'hover:bg-surface-gray-2/70 hover:text-ink-gray-9',
		]"
		@click="handleClick"
	>
		<!-- Collapsed, the item is a centred square as tall as the expanded row,
		     so the icons keep their height when the rail folds. The gap lives only
		     on the expanded branch: a `gap-0` beside a static `gap-2` loses the
		     cascade, which left 8px after the icon and pushed it 4px off-centre.
		     The label goes `sr-only` for the same reason — out of the flex flow,
		     yet still the button's accessible name. -->
		<div
			class="group flex h-11 w-full items-center duration-200 ease-out"
			:class="isCollapsed ? 'relative justify-center' : 'gap-2 px-3'"
		>
			<Tooltip
				:text="__(link.label)"
				placement="right"
				:disabled="!isCollapsed"
			>
				<slot name="icon">
					<span class="grid size-5 flex-shrink-0 place-items-center">
						<component
							:is="typeof link.icon === 'string' ? icons[link.icon] : link.icon"
							class="size-5 stroke-1.5"
							:class="isActive ? 'text-brand' : 'text-ink-gray-6'"
						/>
					</span>
				</slot>
			</Tooltip>
			<Tooltip
				:text="__(link.label)"
				placement="right"
				:disabled="isCollapsed"
				:hoverDelay="1.5"
			>
				<span
					class="min-w-0 truncate text-p-base duration-200 ease-out"
					:class="isCollapsed ? 'sr-only opacity-0' : 'opacity-100'"
				>
					{{ __(link.label) }}
				</span>
			</Tooltip>
			<KeyboardShortcut
				v-if="link.shortcut && !isCollapsed"
				bg
				:combo="link.shortcut"
				class="!ms-auto"
			/>
			<span
				v-if="link.count && !isCollapsed"
				class="!ms-auto block text-p-xs text-ink-gray-5"
				:class="
					isCollapsed && link.count > 9
						? 'absolute top-[2px] end-0 bg-surface-base'
						: ''
				"
			>
				{{ link.count }}
			</span>
			<div
				v-if="showControls && !isCollapsed"
				class="flex items-center gap-x-2 !ms-auto block text-p-xs text-ink-gray-5 group-hover:visible invisible"
			>
				<component
					:is="icons['Edit']"
					class="h-3 w-3 stroke-1.5 text-ink-gray-7"
					@click.stop="openModal(link)"
				/>
				<component
					:is="icons['X']"
					class="h-3 w-3 stroke-1.5 text-ink-gray-7"
					@click.stop="deletePage(link)"
				/>
			</div>
		</div>
	</button>
	<ContactUsEmail v-model="showContactForm" />
</template>
<script setup lang="ts">
import { KeyboardShortcut, Tooltip } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ContactUsEmail from '@/components/ContactUsEmail.vue'
import * as icons from 'lucide-vue-next'
import { toggleNotifications } from '@/stores/notifications'
import { useSettings } from '@/stores/settings'
import type { SidebarLink } from '@/types'
import { openExternal } from '@/utils/openExternal'

const router = useRouter()
const settingsStore = useSettings()
const emit = defineEmits<{
	openModal: [link: SidebarLink]
	deletePage: [link: SidebarLink]
}>()
const showContactForm = ref<boolean>(false)

const props = withDefaults(
	defineProps<{
		link: SidebarLink
		isCollapsed?: boolean
		showControls?: boolean
		activeTab?: string
	}>(),
	{
		isCollapsed: false,
		showControls: false,
		activeTab: '',
	}
)

function handleClick(): void {
	if (props.link.action === 'commandPalette') {
		settingsStore.isCommandPaletteOpen = true
		return
	}
	if (props.link.panel === 'notifications') {
		toggleNotifications()
		return
	}
	if (props.link.to && router.hasRoute(props.link.to)) {
		router.push({ name: props.link.to })
	} else if (props.link.to?.includes('@')) {
		showContactForm.value = true
	} else if (props.link.to) {
		if (props.link.to.startsWith('http')) {
			openExternal(props.link.to)
			return
		}
		window.location.href = `/${props.link.to}`
	}
}

const isActive = computed<boolean>(() => {
	return Boolean(
		props.link?.activeFor?.includes(router.currentRoute.value.name as string) ||
			(props.activeTab && props.link?.label?.includes(props.activeTab))
	)
})

function openModal(link: SidebarLink): void {
	emit('openModal', link)
}

function deletePage(link: SidebarLink): void {
	emit('deletePage', link)
}
</script>
