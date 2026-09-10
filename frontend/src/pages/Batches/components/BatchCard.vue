<template>
	<JGridTile>
		<JGridTileHeading>
			<JGridTileTitle>{{ batch.title }}</JGridTileTitle>
			<template v-if="batch.seat_count" #trailing>
				<Badge
					variant="subtle"
					:theme="batch.seats_left > 0 ? 'green' : 'red'"
					size="sm"
					:label="
						batch.seats_left > 0
							? batch.seats_left +
							  ' ' +
							  (batch.seats_left > 1 ? __('Seats Left') : __('Seat Left'))
							: __('Sold Out')
					"
				/>
			</template>
		</JGridTileHeading>

		<JGridTileDescription v-if="batch.description">
			{{ batch.description }}
		</JGridTileDescription>

		<div class="flex flex-col gap-1 text-p-sm text-ink-gray-6">
			<DateRange :startDate="batch.start_date" :endDate="batch.end_date" />
			<div class="flex items-center gap-1.5">
				<span class="lucide-clock size-3.5 shrink-0" aria-hidden="true" />
				<span dir="ltr">
					{{ formatTime(batch.start_time) }} - {{ formatTime(batch.end_time) }}
				</span>
			</div>
			<div v-if="batch.timezone" class="flex items-center gap-1.5">
				<span class="lucide-globe size-3.5 shrink-0" aria-hidden="true" />
				<span>
					{{
						formatTimezone(
							batch.timezone,
							nextOccurrence(batch.start_date, batch.end_date)
						)
					}}
				</span>
			</div>
		</div>

		<div v-if="batch.instructors?.length" class="flex items-center">
			<div
				class="h-6 me-1"
				:class="{ 'avatar-group overlap': batch.instructors.length > 1 }"
			>
				<UserAvatar
					v-for="instructor in batch.instructors"
					:key="instructor.name"
					:user="instructor"
				/>
			</div>
			<CourseInstructors :instructors="batch.instructors" />
		</div>

		<JGridTileMeta>
			<JGridTileChip v-if="batch.category">{{ batch.category }}</JGridTileChip>
			<template v-if="batch.amount" #end>
				<span class="text-p-xs-medium text-ink-gray-7">{{ batch.price }}</span>
			</template>
		</JGridTileMeta>
	</JGridTile>
</template>
<script setup>
/**
 * The batch card, on the same tile as CourseCard — see that file's note for why
 * the catalogue moved onto jutsu-siem's soc/GridTile.tsx.
 *
 * This one had drifted further than the course card: a 150px floor, a `text-lg`
 * title, its own copy of `.short-introduction` (an unscoped global, so it also
 * reached whatever else happened to use the class), and a seat badge stacked
 * under the title rather than set beside it. The seat count is a status, so it
 * sits where the SIEM puts a status — the heading's trailing slot — and the
 * price moves to the meta rule's end, where a tile's one right-aligned fact
 * goes.
 */
import { Badge } from 'frappe-ui'
import { formatTime } from '@/utils'
import { formatTimezone, nextOccurrence } from '@/utils/timezone'
import DateRange from '@/components/Common/DateRange.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import {
	JGridTile,
	JGridTileChip,
	JGridTileDescription,
	JGridTileHeading,
	JGridTileMeta,
	JGridTileTitle,
} from '@/components/jutsu'

const props = defineProps({
	batch: {
		type: Object,
		default: null,
	},
})
</script>
