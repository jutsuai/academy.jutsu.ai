// `??`, not `||`: an empty string is meaningful — it means the app is mounted at
// the site root (`"lms_path": ""` in site_config) — and `||` would silently turn
// it back into 'lms', leaving the router with a base the URLs never carry and
// every deep link 404ing on reload.
export function getLmsBasePath() {
	return window.lms_path ?? 'lms'
}

/** The router's history base: '/' at the site root, '/lms' under a prefix. */
export function getLmsHistoryBase() {
	const base = getLmsBasePath()
	return base ? `/${base}` : '/'
}

export function getLmsRoute(path = '') {
	const base = getLmsBasePath()
	if (!path) {
		return base ? `/${base}` : '/'
	}
	const normalized = path.startsWith('/') ? path.slice(1) : path
	return base ? `/${base}/${normalized}` : `/${normalized}`
}
