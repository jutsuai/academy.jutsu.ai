// Shrinks an image in the browser before it is uploaded.
//
// Files are stored and served exactly as uploaded: nothing downstream resizes
// or re-encodes them, and the server sends them uncompressed. A pasted
// screenshot or a phone photo therefore costs every learner its full size on
// every first view. Re-encoding as WebP here typically cuts a PNG screenshot
// to a quarter of its size and a multi-megabyte photo far further.
//
// Every failure path returns the original file: an image that uploads at full
// size beats one that does not upload at all.

// The longest side an image keeps. Wide enough for a full-width figure on a
// 2x display; anything larger is detail the page never shows.
const MAX_DIMENSION = 1920
const QUALITY = 0.82

// GIF is left alone because a canvas keeps only its first frame, SVG because
// it is not a raster, and WebP/AVIF because they are already compact.
const COMPRESSIBLE_TYPES = ['image/png', 'image/jpeg']

const encode = (
	canvas: HTMLCanvasElement,
	type: string
): Promise<Blob | null> =>
	new Promise((resolve) => canvas.toBlob(resolve, type, QUALITY))

export async function compressImage(file: File): Promise<File> {
	if (!COMPRESSIBLE_TYPES.includes(file.type)) return file
	if (typeof createImageBitmap !== 'function') return file

	try {
		const bitmap = await createImageBitmap(file)
		const scale = Math.min(
			1,
			MAX_DIMENSION / Math.max(bitmap.width, bitmap.height)
		)
		const canvas = document.createElement('canvas')
		canvas.width = Math.max(1, Math.round(bitmap.width * scale))
		canvas.height = Math.max(1, Math.round(bitmap.height * scale))
		const context = canvas.getContext('2d')
		if (!context) return file
		context.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
		bitmap.close()

		// A browser that cannot encode the requested type silently hands back a
		// PNG instead (Safari, for WebP), so the blob's own type is what counts.
		// A JPEG source can still fall back to a smaller JPEG; a PNG cannot,
		// because JPEG would flatten its transparency.
		let blob = await encode(canvas, 'image/webp')
		if (blob?.type !== 'image/webp' && file.type === 'image/jpeg') {
			blob = await encode(canvas, 'image/jpeg')
		}
		if (!blob || !['image/webp', 'image/jpeg'].includes(blob.type)) return file
		if (blob.size >= file.size) return file

		const extension = blob.type === 'image/webp' ? 'webp' : 'jpg'
		const name = `${file.name.replace(/\.[^.]+$/, '')}.${extension}`
		return new File([blob], name, {
			type: blob.type,
			lastModified: file.lastModified,
		})
	} catch {
		return file
	}
}
