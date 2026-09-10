import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'
import { viteStaticCopy } from 'vite-plugin-static-copy'

// `@framework/ui` is imported by name and resolved through node_modules, so the
// link there is load-bearing rather than a convenience. package.json declares it
// as `link:../../frappe/ui`, which is correct from apps/lms/frontend and wrong
// from a git worktree of this app: that resolves to
// `apps/lms/.lms-worktrees/frappe/ui`, which nothing creates. An install there
// leaves a link into empty space and the only symptom is "Failed to resolve
// import @framework/ui/ConditionBuilder", naming neither the link nor the fix.
//
// Nothing here can repair it, since yarn owns that path, so this says so instead,
// with the command. It asks only whether the link leads anywhere: realpathSync
// throws on a dangling symlink, which is exactly the worktree case. A checkout
// with no frappe app beside it has no link at all and reaches vite's own
// "does the file exist?", which is the right error for a missing source.
function assertFrameworkUiLinked(frontend) {
	const link = path.join(frontend, 'node_modules', '@framework', 'ui')
	try {
		if (fs.statSync(fs.realpathSync(link)).isDirectory()) return
	} catch {
		// falls through to the throw below
	}
	if (!fs.existsSync(path.dirname(link))) return
	throw new Error(
		`@framework/ui at ${link} does not lead anywhere.\n` +
			"package.json's `link:../../frappe/ui` only resolves from apps/lms/frontend.\n" +
			'Repair it with:\n  ln -sfn <path to apps/frappe/ui> ' +
			link,
	)
}

/**
 * Supplies `window.lms_path` to the dev server.
 *
 * In production Frappe renders index.html as a Jinja template and writes the boot
 * values onto `window` from lms/www/_lms.py — `lms_path` among them, which is what
 * src/utils/basePath.js turns into the router's base. Vite serves index.html as a
 * plain file with no template engine behind it, so in dev that value is simply
 * absent and basePath falls back to 'lms'. The result is that the app answers on
 * /lms/... at :8080 while the same site serves it from / at :8000 — the two halves
 * of one dev environment disagreeing about their own URLs.
 *
 * Read from the bench's site config rather than a second env var, so there is one
 * place that decides this and dev cannot drift from the server it is talking to.
 * Both are visible here: docker-compose.dev.yml mounts the bench into this
 * container, and getCommonSiteConfig-style upward traversal is how frappe-ui's own
 * plugin finds it.
 *
 * Silent when it finds nothing — a checkout with no bench beside it still runs,
 * and falls back to the same 'lms' it always did.
 */
function devLmsPath() {
	return {
		name: 'lms-dev-lms-path',
		transformIndexHtml(html, context) {
			// context.server is set only by the dev server; the production build
			// gets its value from Jinja and must not be given a second one.
			if (!context.server) return html
			const lmsPath = readSiteConfig()?.lms_path
			if (lmsPath === undefined) return html
			return html.replace(
				'</head>',
				`\t\t<script>window.lms_path = ${JSON.stringify(lmsPath)}</script>\n\t</head>`,
			)
		},
	}
}

/** The default site's config, found by walking up to the bench root. */
function readSiteConfig() {
	let dir = __dirname
	while (dir !== path.dirname(dir)) {
		const sites = path.join(dir, 'sites')
		if (fs.existsSync(sites) && fs.existsSync(path.join(dir, 'apps'))) {
			try {
				const common = JSON.parse(
					fs.readFileSync(
						path.join(sites, 'common_site_config.json'),
						'utf8',
					),
				)
				const site = common.default_site
				if (!site) return undefined
				return JSON.parse(
					fs.readFileSync(
						path.join(sites, site, 'site_config.json'),
						'utf8',
					),
				)
			} catch {
				return undefined
			}
		}
		dir = path.dirname(dir)
	}
	return undefined
}

export default defineConfig(async ({ mode }) => {
	const isDev = mode === 'development'
	assertFrameworkUiLinked(__dirname)
	const frappeui = await importFrappeUIPlugin(isDev)

	const config = {
		define: {
			__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
		},
		plugins: [
			frappeui({
				frappeProxy: true,
				lucideIcons: true,
				jinjaBootData: true,
				buildConfig: {
					indexHtmlPath: '../lms/www/_lms.html',
				},
			}),
			vue(),
			devLmsPath(),
			VitePWA({
				registerType: 'autoUpdate',
				devOptions: {
					enabled: false,
				},
				workbox: {
					cleanupOutdatedCaches: true,
					maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
					globDirectory: '/assets/lms/frontend',
					globPatterns: ['**/*.{js,ts,css,html,svg}'],
					runtimeCaching: [
						{
							urlPattern: ({ request }) =>
								request.destination === 'document',
							handler: 'NetworkFirst',
							options: {
								cacheName: 'html-cache',
							},
						},
					],
				},
				manifest: false,
			}),
			// pdf.js needs cMaps (JPEG2000/JBIG2 + CJK) and standard_fonts (non-embedded
			// fonts) as sibling assets, or those PDFs render blank and look like a pdf.js
			// bug. Copy them under pdfjs/; PdfBlock.vue points cMapUrl/standardFontDataUrl
			// at `${BASE_URL}pdfjs/...`. Served in dev too (static-copy dev middleware).
			viteStaticCopy({
				targets: [
					{
						src: 'node_modules/pdfjs-dist/cmaps/*',
						dest: 'pdfjs/cmaps',
					},
					{
						src: 'node_modules/pdfjs-dist/standard_fonts/*',
						dest: 'pdfjs/standard_fonts',
					},
				],
			}),
		],
		server: {
			// The linked @framework/ui (apps/frappe/ui) is imported by name and
			// resolved through its `exports`, so in dev vite serves it from source,
			// outside this root, hence the allowance helpdesk makes for it too.
			// Named by resolved path rather than by counting `..` levels: `../..`
			// is apps/ only from apps/lms/frontend, and a worktree of this app sits
			// two levels deeper, where it lands on .lms-worktrees/ and the framework
			// files 403 with "not allowed to be served".
			fs: {
				allow: ['..', '../..', '../../..', '../../../..'],
			},
			host: '0.0.0.0', // Accept connections from any network interface
			allowedHosts: true,
			// SCORM packages are served by Frappe's SCORMRenderer at /scorm/... .
			// frappeProxy only forwards ^/(desk|app|login|api|assets|files|private),
			// so without this the iframe's /scorm URL hits the SPA fallback and renders
			// blank. The `router` mirrors frappeProxy: Frappe resolves the site from the
			// Host header, so we must forward to http://<site>:8000; a bare 127.0.0.1
			// target makes Frappe 404 with "127.0.0.1 does not exist". (Backend :8000.)
			proxy: {
				'/scorm': {
					target: 'http://127.0.0.1:8000',
					router: (req) =>
						`http://${req.headers.host.split(':')[0]}:8000`,
				},
			},
		},
		resolve: {
			// Resolve the linked `@framework/ui` through its symlink rather than its real
			// path. It is `link:../../frappe/ui`, and its own source imports bare deps of
			// its own: `vuedraggable` in ConditionGroup.vue, plus reka-ui, dompurify and
			// frappe-ui. Resolution walks up from the *importer*, so following the link to
			// `apps/frappe/ui/src/...` looks for them under `apps/frappe` — which on a bench
			// has its own node_modules and in CI is a sparse checkout of `ui` alone. Keeping
			// the symlinked path walks up through `apps/lms/frontend/node_modules` instead,
			// where LMS already declares every one of them.
			//
			// So it fails only in CI, which is why it was invisible here: locally
			// `apps/frappe/node_modules/vuedraggable` satisfies the lookup. Both the vitest
			// run and the SPA build hit it, as "Failed to resolve import vuedraggable from
			// ...ConditionGroup.vue". Reproduce it by pointing the link at a copy of
			// apps/frappe/ui that has no node_modules beside it.
			preserveSymlinks: true,
			alias: {
				'@': path.resolve(__dirname, 'src'),
			},
			// Force one copy of prosemirror; duplicate copies break tiptap's
			// instanceof checks and crash the list buttons.
			dedupe: [
				// @framework/ui imports from vue and frappe-ui; a second copy of
				// either would give its Combobox a different frappe-ui than ours.
				'prosemirror-model',
				'prosemirror-state',
				'prosemirror-view',
				'prosemirror-transform',
				'vue',
				'frappe-ui',
			],
		},
		optimizeDeps: {
			include: [
				'feather-icons',
				'tailwind.config.js',
				'highlight.js',
				'plyr',
				'interactjs',
			],
			exclude: mode === 'production' ? [] : ['frappe-ui'],
		},
	}
	return config
})

async function importFrappeUIPlugin(isDev) {
	if (isDev) {
		try {
			const module = await import('../frappe-ui/vite')
			return module.default
		} catch (error) {
			console.warn(
				'Local frappe-ui not found, falling back to npm package:',
				error.message,
			)
		}
	}
	// Fall back to npm package if local import fails
	const module = await import('frappe-ui/vite')
	return module.default
}
