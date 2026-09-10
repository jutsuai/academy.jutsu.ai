<template>
	<div class="w-full">
		<PageHeader :breadcrumbs="[{ label: __('Design system') }]" />

		<div class="space-y-8 p-5">
			<header class="space-y-1">
				<h1 class="text-4xl font-semibold tracking-tight text-ink-gray-9">
					{{ __('Design system') }}
				</h1>
				<p class="text-p-base text-ink-gray-5">
					{{
						__(
							'The Jutsu SIEM component set, ported to Vue. Every control here is the same class stack the SIEM paints with.'
						)
					}}
				</p>
			</header>

			<!-- KPI band — the SIEM's signature opening row -->
			<section class="space-y-3">
				<h2 class="text-lg-medium text-ink-gray-9">{{ __('KPI tiles') }}</h2>
				<JStatBand>
					<JKpiCard
						:label="__('Enrolments (30d)')"
						value="28,609"
						:hint="__('of 176,242 lifetime')"
						tone="brand"
					>
						<template #icon>
							<span class="lucide-database block size-4.5" />
						</template>
					</JKpiCard>
					<JKpiCard
						:label="__('Certificates issued')"
						value="71"
						:hint="__('100 pending review')"
						tone="success"
					>
						<template #icon>
							<span class="lucide-bell block size-4.5" />
						</template>
					</JKpiCard>
					<JKpiCard
						:label="__('Overdue assignments')"
						value="95"
						:hint="__('total')"
						tone="critical"
					>
						<template #icon>
							<span class="lucide-flame block size-4.5" />
						</template>
					</JKpiCard>
				</JStatBand>
			</section>

			<!-- Buttons -->
			<section class="space-y-3">
				<h2 class="text-lg-medium text-ink-gray-9">{{ __('Buttons') }}</h2>
				<JCard>
					<JCardHeader
						:title="__('Variants')"
						:description="
							__(
								'Destructive is tinted, never a solid red fill — the SIEM reserves solid fills for the brand.'
							)
						"
					/>
					<JCardContent class="flex flex-wrap items-center gap-2">
						<JButton>{{ __('Default') }}</JButton>
						<JButton variant="outline">{{ __('Outline') }}</JButton>
						<JButton variant="secondary">{{ __('Secondary') }}</JButton>
						<JButton variant="ghost">{{ __('Ghost') }}</JButton>
						<JButton variant="destructive">{{ __('Delete') }}</JButton>
						<JButton variant="link">{{ __('Link') }}</JButton>
						<JButton loading>{{ __('Saving') }}</JButton>
					</JCardContent>
					<JCardContent class="flex flex-wrap items-center gap-2">
						<JButton size="xs">xs · 24px</JButton>
						<JButton size="sm">sm · 28px</JButton>
						<JButton size="default">default · 32px</JButton>
						<JButton size="lg">lg · 36px</JButton>
						<JButton size="icon" variant="outline" aria-label="Refresh">
							<span class="lucide-refresh-cw block size-4" />
						</JButton>
					</JCardContent>
				</JCard>
			</section>

			<!-- Badges -->
			<section class="space-y-3">
				<h2 class="text-lg-medium text-ink-gray-9">
					{{ __('Badges and status') }}
				</h2>
				<JCard>
					<JCardHeader
						:title="__('Severity')"
						:description="
							__(
								'Full pills at 12% fill. Severity is a property of the thing.'
							)
						"
					/>
					<JCardContent class="flex flex-wrap items-center gap-2">
						<JSeverityBadge
							v-for="level in SEVERITY_LEVELS"
							:key="level"
							:level="level"
							dot
						/>
					</JCardContent>
					<JCardHeader
						:title="__('Workflow status')"
						:description="
							__(
								'Rounded rectangles with an inset ring. Status is where it sits in a pipeline.'
							)
						"
					/>
					<JCardContent class="flex flex-wrap items-center gap-2">
						<JStatusBadge tone="brand" :label="__('New')" />
						<JStatusBadge tone="info" :label="__('In progress')" />
						<JStatusBadge tone="pending" :label="__('Review pending')" />
						<JStatusBadge tone="success" :label="__('Completed')" />
						<JStatusBadge tone="warning" :label="__('Escalated')" />
						<JStatusBadge tone="danger" :label="__('Failed')" />
						<JStatusBadge tone="neutral" :label="__('Closed')" />
					</JCardContent>
					<JCardHeader :title="__('Generic badges and tags')" />
					<JCardContent class="flex flex-wrap items-center gap-2">
						<JBadge>{{ __('Default') }}</JBadge>
						<JBadge variant="secondary">{{ __('Secondary') }}</JBadge>
						<JBadge variant="outline">{{ __('Outline') }}</JBadge>
						<JBadge variant="destructive">{{ __('Destructive') }}</JBadge>
						<JTag>course.published</JTag>
						<JTag>quiz.submitted</JTag>
					</JCardContent>
				</JCard>
			</section>

			<!-- Toolbar -->
			<section class="space-y-3">
				<h2 class="text-lg-medium text-ink-gray-9">
					{{ __('Toolbar, chips and toggles') }}
				</h2>
				<JToolbar>
					<JSearchInput
						v-model="search"
						:placeholder="__('Search courses…')"
					/>
					<JSegmented
						v-model="layout"
						icon-only
						:options="layoutOptions"
					/>
					<JCountPill>171 {{ __('total') }}</JCountPill>
				</JToolbar>
				<JChipGroup>
					<JFilterChip
						v-for="chip in chips"
						:key="chip.label"
						:label="__(chip.label)"
						:count="chip.count"
						:dot="chip.dot"
						:active="activeChip === chip.label"
						@click="activeChip = activeChip === chip.label ? '' : chip.label"
					/>
				</JChipGroup>
			</section>

			<!-- Table -->
			<section class="space-y-3">
				<h2 class="text-lg-medium text-ink-gray-9">{{ __('Table') }}</h2>
				<JCard>
					<JCardHeader
						:title="__('Recent submissions')"
						:description="__('Mono for machine values, tabular figures for counts.')"
						bordered
					>
						<template #actions>
							<JButton size="sm" variant="outline">
								<span class="lucide-list-filter block size-3.5" />
								{{ __('Filter') }}
							</JButton>
						</template>
					</JCardHeader>
					<JTable>
						<thead>
							<tr class="border-b border-outline-gray-2">
								<JTableHead sortable direction="desc">
									{{ __('Severity') }}
								</JTableHead>
								<JTableHead>{{ __('Risk') }}</JTableHead>
								<JTableHead>{{ __('Learner') }}</JTableHead>
								<JTableHead>{{ __('Status') }}</JTableHead>
								<JTableHead>{{ __('Reference') }}</JTableHead>
								<JTableHead numeric>{{ __('Score') }}</JTableHead>
							</tr>
						</thead>
						<tbody>
							<JTableRow
								v-for="row in rows"
								:key="row.learner"
								:selected="row.learner === selectedRow"
							>
								<JTableCell>
									<JSeverityBadge :level="row.severity" />
								</JTableCell>
								<JTableCell>
									<JRiskScore :score="row.risk" />
								</JTableCell>
								<JTableCell>{{ row.learner }}</JTableCell>
								<JTableCell>
									<JStatusBadge :tone="row.tone" :label="__(row.status)" />
								</JTableCell>
								<JTableCell mono>{{ row.reference }}</JTableCell>
								<JTableCell numeric>{{ row.score }}</JTableCell>
							</JTableRow>
						</tbody>
					</JTable>
					<JCardFooter>
						<span class="text-p-sm text-ink-gray-5">
							{{ __('3 of 171') }}
						</span>
					</JCardFooter>
				</JCard>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
/**
 * A live gallery of the ported Jutsu SIEM component set.
 *
 * It exists so the design system is inspectable in the running app rather than
 * only in source: a token change or a component regression shows up here
 * immediately, in both themes, without hunting for a page that happens to use
 * the control. Every section is built from `@/components/jutsu`, so nothing on
 * this page can drift from what the rest of the app renders.
 */
import { ref } from 'vue'
import { usePageMeta } from 'frappe-ui'
import { LayoutGrid, List } from 'lucide-vue-next'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import { SEVERITY_LEVELS } from '@/utils/severity'
import {
	JBadge,
	JButton,
	JCard,
	JCardContent,
	JCardFooter,
	JCardHeader,
	JChipGroup,
	JCountPill,
	JFilterChip,
	JKpiCard,
	JRiskScore,
	JSearchInput,
	JSegmented,
	JSeverityBadge,
	JStatBand,
	JStatusBadge,
	JTable,
	JTableCell,
	JTableHead,
	JTableRow,
	JTag,
	JToolbar,
} from '@/components/jutsu'

const search = ref('')
const layout = ref('list')
const activeChip = ref('Review pending')
const selectedRow = ref('Marcus Oyelaran')

// `iconOnly` renders the icon and drops the label, so a segment without an
// `icon` would draw an empty button. The label stays as the accessible name.
const layoutOptions = [
	{ value: 'grid', label: 'Grid view', icon: LayoutGrid },
	{ value: 'list', label: 'List view', icon: List },
]

const chips = [
	{ label: 'New', count: 0, dot: 'info' },
	{ label: 'In progress', count: 12, dot: 'low' },
	{ label: 'Review pending', count: 11, dot: 'medium' },
	{ label: 'Escalated', count: 38, dot: 'high' },
	{ label: 'Completed', count: 71 },
	{ label: 'Closed', count: 0 },
]

const rows = [
	{
		severity: 'critical',
		risk: 90,
		learner: 'Alice Nakamura',
		status: 'Failed',
		tone: 'danger' as const,
		reference: 'QUIZ-1110.001',
		score: 41,
	},
	{
		severity: 'medium',
		risk: 45,
		learner: 'Marcus Oyelaran',
		status: 'Review pending',
		tone: 'pending' as const,
		reference: 'ASGN-1078.004',
		score: 68,
	},
	{
		severity: 'low',
		risk: 22,
		learner: 'Priya Raman',
		status: 'Completed',
		tone: 'success' as const,
		reference: 'QUIZ-1110.003',
		score: 94,
	},
]

usePageMeta(() => ({ title: 'Design system' }))
</script>
