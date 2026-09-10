/**
 * `useOnboarding` drove the Getting Started panel, which the app no longer has.
 *
 * The composable outlived it, and it is not inert. `updateOnboardingStep` reads
 * the step list that `setUp(steps)` registers:
 *
 *   onboardingStatus.value[user][appName + '_onboarding_status'] =
 *     onboardings[appName].map((s) => …)
 *
 * (node_modules/frappe-ui/frappe/Onboarding/onboarding.js:71-79). With the panel
 * gone nothing calls `setUp`, so `onboardings['learning']` is undefined and that
 * `.map` throws a TypeError.
 *
 * Every caller sat in a form's `onSuccess`, so the throw landed *after* the
 * record was written and before the toast, the list refresh and the close: the
 * row saved, the dialog stayed open, and a second click on Save wrote a
 * duplicate. MemberForm was worse — its onSuccess is inside a try/catch, so a
 * saved member was reported to the user as a failure.
 *
 * A unit test could not see any of this: every suite that mounts one of these
 * forms mocks `frappe-ui/frappe` wholesale, so the throwing function was
 * replaced by `vi.fn()`. Hence a scan of the source rather than a mounted
 * component.
 */
import { describe, expect, it } from 'vitest'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'

const SRC = resolve(process.cwd(), 'src')

const sourceFiles = (dir: string): string[] => {
	const found: string[] = []
	for (const entry of readdirSync(dir)) {
		if (entry === 'node_modules' || entry === 'tests') continue
		const path = join(dir, entry)
		if (statSync(path).isDirectory()) found.push(...sourceFiles(path))
		else if (/\.(vue|ts|js)$/.test(entry)) found.push(path)
	}
	return found
}

describe('onboarding calls', () => {
	const files = sourceFiles(SRC)

	it('reads the component tree the forms live in', () => {
		expect(files.length).toBeGreaterThan(100)
		expect(files.some((f) => f.endsWith('ChapterForm.vue'))).toBe(true)
	})

	it('are gone from src, along with the panel that registered the steps', () => {
		const offenders = files.filter((path) =>
			/useOnboarding|updateOnboardingStep/.test(readFileSync(path, 'utf8'))
		)
		expect(offenders.map((p) => p.slice(SRC.length + 1))).toEqual([])
	})
})
