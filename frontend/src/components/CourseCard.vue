<template>
	<JGridTile v-if="course.title" class="gap-0 overflow-hidden p-0">
		<!-- A course is chosen by its artwork, so the cover leads, full width,
			 the way it always has. What changed is only its SIZE: a fixed 128px
			 band rather than a 168px one on a card with a 350px floor. Fixed
			 rather than a ratio on purpose — the grid runs one to four columns, and
			 a 16/9 cover in a 410px column is 230px of image before a word of text.
		-->
		<div
			class="h-32 w-full shrink-0 bg-cover bg-center bg-no-repeat"
			:style="
				course.image
					? { backgroundImage: `url('${encodeURI(course.image)}')` }
					: { backgroundImage: gradientColor }
			"
		>
			<div
				v-if="!course.image"
				class="flex h-full items-center justify-center px-4 text-center text-lg-semibold leading-snug text-white"
			>
				{{ course.title }}
			</div>
		</div>

		<div class="flex min-h-0 flex-1 flex-col gap-2 p-3">
			<JGridTileHeading>
				<JGridTileTitle>{{ course.title }}</JGridTileTitle>
				<p class="truncate text-p-xs text-ink-gray-5">
					{{ instructorNames }}
				</p>
				<template v-if="course.featured" #trailing>
					<Tooltip :text="__('Featured')">
						<span class="lucide-award size-4 block text-ink-amber-6" />
					</Tooltip>
				</template>
			</JGridTileHeading>

			<JGridTileDescription v-if="course.short_introduction">
				{{ course.short_introduction }}
			</JGridTileDescription>

			<div v-if="user && course.membership" class="flex items-center gap-2">
				<ProgressBar
					:progress="course.membership.progress"
					class="min-w-0 flex-1"
				/>
				<span class="shrink-0 text-p-xs tabular-nums text-ink-gray-5">
					{{ Math.ceil(course.membership.progress) }}%
				</span>
			</div>

			<JGridTileMeta>
				<JGridTileChip v-if="course.lessons" :title="__('Lessons')">
					<span class="lucide-book-open size-3" aria-hidden="true" />
					{{ course.lessons }}
				</JGridTileChip>
				<JGridTileChip
					v-if="course.enrollments"
					:title="__('Enrolled Students')"
				>
					<span class="lucide-users size-3" aria-hidden="true" />
					{{ formatAmount(course.enrollments) }}
				</JGridTileChip>
				<JGridTileChip v-if="course.rating" :title="__('Average Rating')">
					<LucideStar class="size-3 fill-yellow-500 text-transparent" />
					{{ formatRating(course.rating) }}
				</JGridTileChip>
				<template #end>
					<span
						v-if="course.paid_course"
						class="text-p-xs-medium text-ink-gray-7"
					>
						{{ course.price }}
					</span>
					<Tooltip
						v-if="course.paid_certificate || course.enable_certification"
						:text="__('Get Certified')"
					>
						<span class="lucide-graduation-cap size-4 block text-ink-gray-6" />
					</Tooltip>
				</template>
			</JGridTileMeta>
		</div>
	</JGridTile>
</template>

<script setup>
/**
 * The catalogue card, on the SIEM's results tile — the same object as
 * jutsu-siem apps/web/src/components/assets/ConnectedAssetCard.tsx, which is
 * built from soc/GridTile.tsx.
 *
 * It takes that card's chrome and typographic scale — one hairline border, a
 * fill mixed 4.5% toward the foreground, a brand border on hover, a 14px medium
 * title, a two-line blurb, and the counts demoted to chips on a footer rule
 * pinned with `mt-auto` so a grid row shares one baseline.
 *
 * What it does NOT take is the SIEM's anatomy, and that is deliberate: an asset
 * is identified by its name, a course by its artwork, so the cover leads at full
 * width the way a catalogue card should. The old card was not wrong to put it
 * there — it was wrong to be 350px tall with a `text-2xl` title, which in a
 * four-column grid is a poster, not a result. The cover is a fixed 128px band
 * now and the body is dense; the card is roughly a third of its old height.
 */
import { sessionStore } from '@/stores/session'
import { Tooltip } from 'frappe-ui'
import { formatAmount, formatRating } from '@/utils'
import { computed } from 'vue'
import ProgressBar from '@/components/ProgressBar.vue'
import {
	JGridTile,
	JGridTileChip,
	JGridTileDescription,
	JGridTileHeading,
	JGridTileMeta,
	JGridTileTitle,
} from '@/components/jutsu'

const { user } = sessionStore()

const props = defineProps({
	course: {
		type: Object,
		default: null,
	},
})

const gradientColor = computed(() => {
	let color = props.course.card_gradient?.toLowerCase() || 'blue'
	return `linear-gradient(to top right, black, var(--${color}-400))`
})

// A line of names rather than a stack of avatars: at this tile size the avatar
// group was wider than the name it labelled, and the SIEM's equivalent line is
// the plain catalogue name under the title.
const instructorNames = computed(() =>
	(props.course.instructors ?? [])
		.map((i) => i.full_name || i.username || i.name)
		.join(', ')
)
</script>
