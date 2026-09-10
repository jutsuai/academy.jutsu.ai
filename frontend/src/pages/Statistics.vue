<template>
	<div class="">
		<PageHeader :breadcrumbs="breadcrumbs" />
		<div
			v-if="chartDetails.loading && !chartDetails.data"
			class="flex flex-1 items-center justify-center p-5"
		>
			<LoadingIndicator class="size-5 text-ink-gray-5" />
		</div>
		<div v-else-if="chartDetails.data" class="p-5">
			<!-- jutsu-siem apps/web/src/components/soc/KpiCard.tsx, as the SIEM's
				 Dashboard, Alerts and Assets pages all open. frappe-ui's
				 NumberChart in a bare `border rounded-md` gave five identical grey
				 boxes; the tinted icon chip and the 7% wash are what let a reader
				 tell them apart at a glance, and are the whole reason the SIEM's
				 dashboards read the way they do. Tones follow the app's own
				 semantics: signups and enrolments are neutral counts, completions
				 and certifications are outcomes. -->
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
				<JKpiCard
					v-for="kpi in kpis"
					:key="kpi.label"
					:label="kpi.label"
					:value="kpi.value"
					:hint="kpi.hint"
					:tone="kpi.tone"
				>
					<template #icon>
						<span :class="[kpi.icon, 'size-4.5']" />
					</template>
				</JKpiCard>
			</div>
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
				<div class="border rounded-md min-h-72">
					<AxisChart
						v-if="signupsChart.data"
						:config="{
							data: signupsChart.data,
							title: 'Signups',
							subtitle: 'Signups per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Signups',
							},
							series: [{ name: 'signups', type: 'line', showDataPoints: true }],
						}"
					/>
				</div>
				<div class="border rounded-md min-h-72">
					<AxisChart
						v-if="enrollmentChart.data"
						:config="{
							data: enrollmentChart.data,
							title: 'Enrollments',
							subtitle: 'Enrollments per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Enrollments',
							},
							series: [
								{ name: 'enrollments', type: 'line', showDataPoints: true },
							],
						}"
					/>
				</div>
				<div class="border rounded-md">
					<AxisChart
						v-if="certification.data"
						:config="{
							data: certification.data,
							title: 'Certifications',
							subtitle: 'Certifications per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Certifications',
							},
							series: [
								{
									name: 'certifications',
									type: 'line',
									showDataPoints: true,
								},
							],
						}"
					/>
				</div>
				<div v-if="hasCompletions" class="border rounded-md">
					<DonutChart
						v-if="courseCompletion.data"
						:config="{
							data: courseCompletion.data,
							title: 'Completions',
							subtitle: 'Course Completion',
							categoryColumn: 'label',
							valueColumn: 'value',
						}"
					/>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	AxisChart,
	createResource,
	DonutChart,
	LoadingIndicator,
	usePageMeta,
} from 'frappe-ui'
import { computed } from 'vue'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import { JKpiCard } from '@/components/jutsu'
import { sessionStore } from '../stores/session'

const { brand } = sessionStore()

const breadcrumbs = computed(() => {
	return [
		{
			label: __('Statistics'),
			route: {
				name: 'Statistics',
			},
		},
	]
})

const chartDetails = createResource({
	url: 'lms.lms.api.get_chart_details',
	cache: ['statistics'],
	auto: true,
})

// The five headline counts, as SIEM KPI tiles. `hint` carries the phrasing the
// old Tooltip did — a tooltip is the wrong place for a label the reader needs
// in order to know what the number counts, and on a touch screen there is no
// hover to reveal it at all.
const kpis = computed(() => {
	const d = chartDetails.data ?? {}
	return [
		{
			label: __('Courses'),
			value: d.courses,
			hint: __('Published'),
			tone: 'brand',
			icon: 'lucide-book-open',
		},
		{
			label: __('Signups'),
			value: d.users,
			hint: __('Active members'),
			tone: 'default',
			icon: 'lucide-user-plus',
		},
		{
			label: __('Enrollments'),
			value: d.enrollments,
			hint: __('Across all courses'),
			tone: 'default',
			icon: 'lucide-users',
		},
		{
			label: __('Completions'),
			value: d.completions,
			hint: __('Courses finished'),
			tone: 'success',
			icon: 'lucide-circle-check',
		},
		{
			label: __('Certifications'),
			value: d.certifications,
			hint: __('Certified members'),
			tone: 'success',
			icon: 'lucide-award',
		},
	]
})

const signupsChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	params: {
		chart_name: 'New Signups',
	},
	auto: true,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				signups: item.count,
			}
		})
	},
})

const enrollmentChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	cache: ['enrollments'],
	params: {
		chart_name: 'Course Enrollments',
	},
	auto: true,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				enrollments: item.count,
			}
		})
	},
})

const certification = createResource({
	url: 'lms.lms.utils.get_chart_data',
	cache: ['certifications'],
	params: {
		chart_name: 'Certification',
	},
	auto: true,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				certifications: item.count,
			}
		})
	},
})

const courseCompletion = createResource({
	url: 'lms.lms.utils.get_course_completion_data',
	auto: true,
	cache: ['courseCompletion'],
})

// A donut with zero completions conveys nothing, so hide it until at least one
// learner has completed a course.
const hasCompletions = computed(() => {
	const completed = courseCompletion.data?.find((d) => d.label === 'Completed')
	return (completed?.value || 0) > 0
})

usePageMeta(() => {
	return {
		title: __('Statistics'),
		icon: brand.favicon,
	}
})
</script>
