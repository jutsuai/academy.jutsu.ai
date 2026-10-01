import { afterEach, describe, expect, it, vi } from 'vitest'
import { compressImage } from '@/utils/compressImage'

// jsdom has neither createImageBitmap nor a canvas backend, so both are stubbed:
// the bitmap reports the source dimensions and toBlob returns whatever the
// "browser" under test would encode.
const stubBrowser = (
	bitmap: { width: number; height: number },
	encoded: (type: string) => Blob | null
) => {
	vi.stubGlobal(
		'createImageBitmap',
		vi.fn(async () => ({ ...bitmap, close: () => {} }))
	)
	const canvases: HTMLCanvasElement[] = []
	const create = document.createElement.bind(document)
	vi.spyOn(document, 'createElement').mockImplementation(((tag: string) => {
		const element = create(tag)
		if (tag === 'canvas') {
			const canvas = element as HTMLCanvasElement
			canvas.getContext = (() => ({ drawImage: () => {} })) as any
			canvas.toBlob = ((done: BlobCallback, type: string) =>
				done(encoded(type))) as any
			canvases.push(canvas)
		}
		return element
	}) as any)
	return canvases
}

const fileOf = (name: string, type: string, bytes: number) =>
	new File([new Uint8Array(bytes)], name, { type })

const blobOf = (type: string, bytes: number) =>
	new Blob([new Uint8Array(bytes)], { type })

afterEach(() => {
	vi.unstubAllGlobals()
	vi.restoreAllMocks()
})

describe('compressImage', () => {
	it('re-encodes a PNG as a smaller WebP and renames it', async () => {
		stubBrowser({ width: 1112, height: 631 }, (type) => blobOf(type, 100))
		const out = await compressImage(fileOf('Shot (1).png', 'image/png', 400))
		expect(out.type).toBe('image/webp')
		expect(out.name).toBe('Shot (1).webp')
		expect(out.size).toBe(100)
	})

	it('caps the longest side and keeps the aspect ratio', async () => {
		const canvases = stubBrowser({ width: 4000, height: 3000 }, (type) =>
			blobOf(type, 100)
		)
		await compressImage(fileOf('photo.jpg', 'image/jpeg', 400))
		expect([canvases[0].width, canvases[0].height]).toEqual([1920, 1440])
	})

	it('never upscales a small image', async () => {
		const canvases = stubBrowser({ width: 300, height: 200 }, (type) =>
			blobOf(type, 100)
		)
		await compressImage(fileOf('icon.png', 'image/png', 400))
		expect([canvases[0].width, canvases[0].height]).toEqual([300, 200])
	})

	it('keeps the original when the result is not smaller', async () => {
		stubBrowser({ width: 100, height: 100 }, (type) => blobOf(type, 500))
		const file = fileOf('tiny.png', 'image/png', 400)
		expect(await compressImage(file)).toBe(file)
	})

	// A browser without a WebP encoder answers toBlob('image/webp') with a PNG.
	const noWebp = (type: string) =>
		blobOf(type === 'image/webp' ? 'image/png' : type, 100)

	it('falls back to JPEG for a JPEG source when WebP is unavailable', async () => {
		stubBrowser({ width: 4000, height: 3000 }, noWebp)
		const out = await compressImage(fileOf('photo.jpeg', 'image/jpeg', 400))
		expect(out.type).toBe('image/jpeg')
		expect(out.name).toBe('photo.jpg')
	})

	it('leaves a PNG untouched when WebP is unavailable', async () => {
		stubBrowser({ width: 4000, height: 3000 }, noWebp)
		const file = fileOf('shot.png', 'image/png', 400)
		expect(await compressImage(file)).toBe(file)
	})

	it.each([
		['anim.gif', 'image/gif'],
		['logo.svg', 'image/svg+xml'],
		['clip.mp4', 'video/mp4'],
		['done.webp', 'image/webp'],
	])('passes %s through without decoding it', async (name, type) => {
		stubBrowser({ width: 10, height: 10 }, (t) => blobOf(t, 1))
		const file = fileOf(name, type, 400)
		expect(await compressImage(file)).toBe(file)
		expect(createImageBitmap).not.toHaveBeenCalled()
	})

	it('returns the original when the image cannot be decoded', async () => {
		vi.stubGlobal(
			'createImageBitmap',
			vi.fn(async () => {
				throw new Error('corrupt')
			})
		)
		const file = fileOf('broken.png', 'image/png', 400)
		expect(await compressImage(file)).toBe(file)
	})

	it('returns the original when the browser has no createImageBitmap', async () => {
		vi.stubGlobal('createImageBitmap', undefined)
		const file = fileOf('shot.png', 'image/png', 400)
		expect(await compressImage(file)).toBe(file)
	})
})
