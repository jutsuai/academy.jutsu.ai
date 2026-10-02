// How a quiz or an assignment tells the lesson page it just saved progress.
//
// Both complete a lesson by calling mark_lesson_progress themselves, and both
// are mounted as standalone Vue apps inside EditorJS blocks, outside the lesson
// page's component tree — so there is no prop, emit or provide to carry the
// news. The page used to hear it only over the realtime socket, which is not
// reachable on every deployment (nothing proxies the socket.io port behind
// Traefik): the lesson was completed server-side, but Next stayed hidden until
// a manual refresh. A window event needs nothing but the page itself.

const LESSON_PROGRESS_EVENT = 'lms:lesson-progress'

export type LessonProgressDetail = {
	course: string
	// The member's course progress, when the server returned it.
	progress?: number
}

export function announceLessonProgress(detail: LessonProgressDetail): void {
	window.dispatchEvent(new CustomEvent(LESSON_PROGRESS_EVENT, { detail }))
}

/** Subscribes to announcements; returns the function that unsubscribes. */
export function onLessonProgressAnnounced(
	handler: (detail: LessonProgressDetail) => void
): () => void {
	const listener = (event: Event) =>
		handler((event as CustomEvent<LessonProgressDetail>).detail)
	window.addEventListener(LESSON_PROGRESS_EVENT, listener)
	return () => window.removeEventListener(LESSON_PROGRESS_EVENT, listener)
}
