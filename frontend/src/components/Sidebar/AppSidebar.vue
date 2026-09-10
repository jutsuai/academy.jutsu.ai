<template>
	<div
		class="flex h-full flex-col justify-between transition-all duration-300 ease-in-out border-e overflow-x-hidden"
		:class="sidebarStore.isSidebarCollapsed ? 'w-14' : 'w-64'"
	>
		<div
			class="flex flex-col overflow-y-auto flex-1 min-h-0"
			:class="sidebarStore.isSidebarCollapsed ? 'items-center' : ''"
		>
			<UserDropdown :isCollapsed="sidebarStore.isSidebarCollapsed" />
			<div class="flex flex-col" v-if="sidebarSettings.data">
				<div v-for="link in sidebarLinks" class="px-2 py-1">
					<div
						v-if="!link.hideLabel"
						class="flex h-8 shrink-0 items-center gap-1.5 px-3 text-xs font-medium text-ink-gray-5 transition-all duration-200 ease-out"
					>
						<span class="truncate">{{ __(link.label) }}</span>
					</div>
					<nav class="flex flex-col gap-0.5">
						<div v-for="item in link.items">
							<SidebarLink
								:link="item"
								:isCollapsed="sidebarStore.isSidebarCollapsed"
							/>
						</div>
					</nav>
				</div>
			</div>
			<div
				v-if="sidebarSettings.data?.web_pages?.length || isModerator"
				class="mt-4"
			>
				<div
					class="flex items-center justify-between pe-2 cursor-pointer"
					:class="sidebarStore.isSidebarCollapsed ? 'ps-3' : 'ps-4'"
					@click="toggleWebPages"
				>
					<div
						v-if="!sidebarStore.isSidebarCollapsed"
						class="flex items-center text-ink-gray-5 my-1"
					>
						<span class="grid h-5 w-6 flex-shrink-0 place-items-center">
							<span
								class="lucide-chevron-right h-4 w-4 text-ink-gray-9 transition-all duration-300 ease-in-out"
								:class="{
									'rotate-90': !sidebarStore.isWebpagesCollapsed,
									'rtl:rotate-180': sidebarStore.isWebpagesCollapsed,
								}"
							/>
						</span>
						<span class="ms-2">
							{{ __('More') }}
						</span>
					</div>
					<Button
						v-if="isModerator && !readOnlyMode"
						variant="ghost"
						@click="openPageModal()"
					>
						<template #icon>
							<span class="lucide-plus h-4 w-4 text-ink-gray-7" />
						</template>
					</Button>
				</div>
				<div
					v-if="sidebarSettings.data?.web_pages?.length"
					class="flex flex-col transition-all duration-300 ease-in-out"
					:class="!sidebarStore.isWebpagesCollapsed ? 'block' : 'hidden'"
				>
					<div
						v-for="link in sidebarSettings.data.web_pages"
						class="mx-2 my-0.5"
					>
						<SidebarLink
							:link="link"
							:isCollapsed="sidebarStore.isSidebarCollapsed"
							:showControls="isModerator ? true : false"
							@openModal="openPageModal"
							@deletePage="deletePage"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="m-2 flex flex-col gap-1">
			<div
				v-if="readOnlyMode && !sidebarStore.isSidebarCollapsed"
				class="z-10 m-2 bg-surface-elevation-2 py-2.5 px-3 text-p-xs text-ink-gray-7 rounded-md"
			>
				{{
					__(
						'This site is being updated. You will not be able to make any changes. Full access will be restored shortly.'
					)
				}}
			</div>
			<div
				v-if="
					isStudent && !profileIsComplete && !sidebarStore.isSidebarCollapsed
				"
				class="flex flex-col gap-3 text-ink-gray-9 py-2.5 px-3 bg-surface-base shadow-sm rounded-md"
			>
				<div class="flex flex-col text-p-sm gap-1">
					<div class="inline-flex gap-1">
						<span class="lucide-user h-4 my-0.5 shrink-0" />
						<div class="font-medium">
							{{ __('Complete your profile') }}
						</div>
					</div>
					<div class="text-ink-gray-7">
						{{ __('Highlight what makes you unique and show your skills.') }}
					</div>
				</div>
				<router-link
					:to="{
						name: 'Profile',
						params: {
							username: userResource.data?.username,
						},
					}"
				>
					<Button :label="__('My Profile')" class="w-full">
						<template #prefix>
							<span class="lucide-chevrons-right h-4 w-4 text-ink-gray-7" />
						</template>
					</Button>
				</router-link>
			</div>
			<Tooltip
				v-if="
					isStudent && !profileIsComplete && sidebarStore.isSidebarCollapsed
				"
				:text="__('Complete your profile')"
			>
				<router-link
					:to="{
						name: 'Profile',
						params: {
							username: userResource.data?.username,
						},
					}"
					class="flex items-center justify-center"
				>
					<span class="lucide-user size-4 text-ink-gray-7 cursor-pointer" />
				</router-link>
			</Tooltip>
			<TrialBanner
				v-if="
					userResource.data?.is_system_manager && userResource.data?.is_fc_site
				"
				:isSidebarCollapsed="sidebarStore.isSidebarCollapsed"
			/>

			<div
				class="flex items-center mt-4"
				:class="
					sidebarStore.isSidebarCollapsed ? 'flex-col space-y-3' : 'flex-row'
				"
			>
				<div
					class="flex items-center flex-1 gap-3"
					:class="sidebarStore.isSidebarCollapsed ? 'flex-col' : 'flex-row'"
				>
					<Tooltip v-if="readOnlyMode && sidebarStore.isSidebarCollapsed">
						<span
							class="lucide-circle-alert size-4 text-ink-gray-6"
						/>
						<template #body>
							<div
								class="max-w-[30ch] rounded bg-surface-gray-10 px-2 py-1 text-center text-p-xs text-ink-base shadow-xl"
							>
								{{
									__(
										'This site is being updated. You will not be able to make any changes. Full access will be restored shortly.'
									)
								}}
							</div>
						</template>
					</Tooltip>
					<Tooltip
						v-if="showAppointmentIcon"
						:text="__('Book a free onboarding session with the Frappe team')"
					>
						<button
							type="button"
							:aria-label="__('Book a free onboarding session with the Frappe team')"
							class="grid size-7 shrink-0 place-items-center rounded-3 text-ink-gray-6 transition-colors hover:bg-surface-gray-2 hover:text-ink-gray-9 focus:outline-none focus-visible:focus-ring-blue"
							@click="redirectToAppointmentScreen()"
						>
							<span class="lucide-phone size-4" aria-hidden="true" />
						</button>
					</Tooltip>
					<Tooltip :text="__('Powered by Frappe Learning')">
						<button
							type="button"
							:aria-label="__('Powered by Frappe Learning')"
							class="grid size-7 shrink-0 place-items-center rounded-3 text-ink-gray-6 transition-colors hover:bg-surface-gray-2 hover:text-ink-gray-9 focus:outline-none focus-visible:focus-ring-blue"
							@click="redirectToWebsite()"
						>
							<span class="lucide-zap size-4" aria-hidden="true" />
						</button>
					</Tooltip>
				</div>
				<Tooltip
					:text="
						sidebarStore.isSidebarCollapsed ? __('Expand') : __('Collapse')
					"
				>
					<button
						type="button"
						:aria-label="
							sidebarStore.isSidebarCollapsed ? __('Expand') : __('Collapse')
						"
						:aria-expanded="!sidebarStore.isSidebarCollapsed"
						class="grid size-7 shrink-0 place-items-center rounded-3 text-ink-gray-6 transition-colors hover:bg-surface-gray-2 hover:text-ink-gray-9 focus:outline-none focus-visible:focus-ring-blue"
						@click="toggleSidebar()"
					>
						<CollapseSidebar
							class="size-4 stroke-1.5 duration-300 ease-in-out"
							aria-hidden="true"
							:style="{
								transform:
									isRtl !== sidebarStore.isSidebarCollapsed
										? 'rotateY(180deg)'
										: '',
							}"
						/>
					</button>
				</Tooltip>
			</div>
		</div>
	</div>
	<CommandPalette v-model="settingsStore.isCommandPaletteOpen" />
	<PageModal
		v-model="showPageModal"
		v-model:reloadSidebar="sidebarSettings"
		:page="pageToEdit"
	/>
</template>

<script setup>
import { getSidebarLinks } from '@/utils'
import { usersStore } from '@/stores/user'
import { useSidebar } from '@/stores/sidebar'
import { useSettings } from '@/stores/settings'
import { Button, call, Tooltip, toast } from 'frappe-ui'
import PageModal from '@/components/Modals/PageModal.vue'
import LMSLogo from '@/components/Icons/LMSLogo.vue'
import { useRouter } from 'vue-router'
import { openFormRoute } from '@/composables/useFormRoute'
import {
	ref,
	onMounted,
	inject,
	watch,
	reactive,
	markRaw,
	h,
	onUnmounted,
	computed,
} from 'vue'
import {
	BookOpen,
	CircleHelp,
	FolderTree,
	FileText,
	UserPlus,
	Users,
	BookText,
} from 'lucide-vue-next'
import { TrialBanner, useTelemetry } from 'frappe-ui/frappe'
import InviteIcon from '@/components/Icons/InviteIcon.vue'
import UserDropdown from '@/components/Sidebar/UserDropdown.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import SidebarLink from '@/components/Sidebar/SidebarLink.vue'
import CommandPalette from '@/components/CommandPalette/CommandPalette.vue'
import { openExternal } from '@/utils/openExternal'
import {
	loadUnreadCount,
	unreadCount,
	unreadNotifications,
} from '@/stores/notifications'

const { userResource } = usersStore()
let sidebarStore = useSidebar()
const socket = inject('$socket')
const sidebarLinks = ref(null)
const { capture } = useTelemetry()
const showPageModal = ref(false)
const isModerator = ref(false)
const isInstructor = ref(false)
const pageToEdit = ref(null)
const {
	sidebarSettings,
	activeTab,
	isSettingsOpen,
	programs,
	loadSidebarSettings,
} = useSettings()
const settingsStore = useSettings()
const router = useRouter()
const readOnlyMode = window.read_only_mode
const isRtl = document.documentElement.dir === 'rtl'
onMounted(() => {
	addKeyboardShortcut()
	updateSidebarLinks()
	loadUnreadCount()
	socket.on('publish_lms_notifications', () => {
		unreadNotifications.reload()
	})
})

// The count lives in stores/notifications now, so the badge follows it rather
// than being written from the resource's onSuccess.
watch(unreadCount, () => updateUnreadCount())

const updateSidebarLinksVisibility = () => {
	loadSidebarSettings().then(() => {
		const data = sidebarSettings.data
		if (!data) return
		Object.keys(data).forEach((key) => {
			if (!parseInt(data[key])) {
				sidebarLinks.value.forEach((link) => {
					link.items = link.items.filter(
						(item) => item.label.toLowerCase().split(' ').join('_') !== key
					)
				})
			}
		})
	})
}

const addKeyboardShortcut = () => {
	window.addEventListener('keydown', (e) => {
		if (
			e.key === 'k' &&
			(e.ctrlKey || e.metaKey) &&
			!e.target.classList.contains('ProseMirror')
		) {
			toggleCommandPalette()
			e.preventDefault()
		}
	})
}

const toggleCommandPalette = () => {
	settingsStore.isCommandPaletteOpen = !settingsStore.isCommandPaletteOpen
}

const updateUnreadCount = () => {
	sidebarLinks.value?.forEach((link) => {
		link.items.forEach((item) => {
			if (item.label === 'Notifications') {
				item.count = unreadCount.value || 0
			}
		})
	})
}

const openPageModal = (link) => {
	showPageModal.value = true
	pageToEdit.value = link
}

const deletePage = (link) => {
	call('lms.lms.api.delete_documents', {
		doctype: 'LMS Sidebar Item',
		documents: [link.name],
	}).then(() => {
		loadSidebarSettings(true)
		toast.success(__('Page deleted successfully'))
	})
}

const toggleSidebar = () => {
	sidebarStore.isSidebarCollapsed = !sidebarStore.isSidebarCollapsed
	localStorage.setItem(
		'isSidebarCollapsed',
		JSON.stringify(sidebarStore.isSidebarCollapsed)
	)
}

const toggleWebPages = () => {
	sidebarStore.isWebpagesCollapsed = !sidebarStore.isWebpagesCollapsed
	localStorage.setItem(
		'isWebpagesCollapsed',
		JSON.stringify(sidebarStore.isWebpagesCollapsed)
	)
}

watch(userResource, async () => {
	await userResource.promise
	if (userResource.data) {
		isModerator.value = userResource.data.is_moderator
		isInstructor.value = userResource.data.is_instructor
		await programs.reload()
	}
	updateSidebarLinks()
})

watch(settingsStore.settings, () => {
	updateSidebarLinks()
})

watch(
	() => sidebarSettings.data,
	() => updateSidebarLinks(),
	{ deep: true }
)

const updateSidebarLinks = () => {
	sidebarLinks.value = getSidebarLinks()
	updateSidebarLinksVisibility()
	updateUnreadCount()
}

const redirectToWebsite = () => {
	openExternal('https://frappe.io/learning')
}

const isStudent = computed(() => {
	return userResource.data?.is_student
})

const profileIsComplete = computed(() => {
	return (
		userResource.data?.user_image &&
		userResource.data?.headline &&
		userResource.data?.bio
	)
})

const showAppointmentIcon = computed(() => {
	let isTrialPlan = userResource.data?.site_info?.plan?.is_trial_plan
	let trialEndDate = calculateTrialEndDays(
		userResource.data?.site_info?.trial_end_date
	)
	return (
		userResource.data?.is_system_manager &&
		userResource.data?.is_fc_site &&
		isTrialPlan &&
		trialEndDate > 0
	)
})

const calculateTrialEndDays = (trialEndDate) => {
	if (!trialEndDate) return 0

	trialEndDate = new Date(trialEndDate)
	const today = new Date()
	const diffTime = trialEndDate - today
	const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
	return diffDays
}

const redirectToAppointmentScreen = () => {
	openExternal(
		'https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ0c7Z3XIpW1WgbeIuktSaoX6qudoYuSdRbIlJty5TW7p4IZaOk5viHQGwTNi6HpNVqzOZOTHcle'
	)
}

onUnmounted(() => {
	socket.off('publish_lms_notifications')
})
</script>
