import { reactive } from 'vue'

// What the lesson page offers to blocks mounted outside its component tree.
//
// A quiz is a standalone Vue app inside an EditorJS block, so it cannot be
// handed the page's Next handler as a prop or inject it. Vue reactivity is not
// scoped to an app, though: the page writes here, and the quiz summary reads it
// to offer "Next lesson" beside "Try Again" the moment the lesson unlocks.
// Empty whenever no lesson page is mounted, which is what keeps the button off
// the standalone quiz page.
export const lessonNav = reactive<{
	canGoNext: boolean
	goNext: (() => void) | null
}>({
	canGoNext: false,
	goNext: null,
})
