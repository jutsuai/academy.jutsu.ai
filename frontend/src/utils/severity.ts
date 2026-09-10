/**
 * Severity vocabulary and its Tailwind class maps, ported from
 * jutsu-siem/apps/web/src/lib/severity.ts.
 *
 * The colours themselves are the `--sev-*` tokens in styles/jutsuTokens.css;
 * this is the mapping layer that turns a level into the exact class strings the
 * SIEM paints with. Every class is written out as a complete literal because
 * Tailwind only generates classes it can find as whole strings in source — a
 * template like `text-sev-${level}` compiles to nothing.
 */

export const SEVERITY_LEVELS = [
	'critical',
	'high',
	'medium',
	'low',
	'info',
] as const

export type Severity = (typeof SEVERITY_LEVELS)[number]

const ORDER: Record<Severity, number> = {
	critical: 0,
	high: 1,
	medium: 2,
	low: 3,
	info: 4,
}

const TEXT_CLASS: Record<Severity, string> = {
	critical: 'text-sev-critical',
	high: 'text-sev-high',
	medium: 'text-sev-medium',
	low: 'text-sev-low',
	info: 'text-sev-info',
}

/** Tinted fill + coloured text + a matching border — the SIEM's outlined badge. */
const BADGE_CLASS: Record<Severity, string> = {
	critical: 'bg-sev-critical/12 text-sev-critical border-sev-critical/30',
	high: 'bg-sev-high/12 text-sev-high border-sev-high/30',
	medium: 'bg-sev-medium/12 text-sev-medium border-sev-medium/30',
	low: 'bg-sev-low/12 text-sev-low border-sev-low/30',
	info: 'bg-sev-info/12 text-sev-info border-sev-info/30',
}

const DOT_CLASS: Record<Severity, string> = {
	critical: 'bg-sev-critical',
	high: 'bg-sev-high',
	medium: 'bg-sev-medium',
	low: 'bg-sev-low',
	info: 'bg-sev-info',
}

/** Coerce any string to a known level, defaulting to `info`. */
export function normalizeSeverity(level?: string): Severity {
	const value = (level ?? 'info').toLowerCase()
	if (!value || value === 'informational' || value === 'unknown') return 'info'
	if (value === 'fatal') return 'critical'
	return (SEVERITY_LEVELS as readonly string[]).includes(value)
		? (value as Severity)
		: 'info'
}

/** A 0–100 score banded onto the ramp — the SIEM's bands, unchanged. */
export function severityFromScore(score: number): Severity {
	if (score <= 20) return 'info'
	if (score <= 40) return 'low'
	if (score <= 60) return 'medium'
	if (score <= 80) return 'high'
	return 'critical'
}

/** `var(--sev-*)`, for inline `style` fills such as chart bars. */
export const severityColorVar = (level?: string): string =>
	`var(--sev-${normalizeSeverity(level)})`

export const severityTextClass = (level?: string): string =>
	TEXT_CLASS[normalizeSeverity(level)]

export const severityBadgeClass = (level?: string): string =>
	BADGE_CLASS[normalizeSeverity(level)]

export const severityDotClass = (level?: string): string =>
	DOT_CLASS[normalizeSeverity(level)]

/** Sort key — critical first. */
export const severityOrder = (level?: string): number =>
	ORDER[normalizeSeverity(level)]
