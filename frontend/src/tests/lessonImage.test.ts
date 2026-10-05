import { beforeEach, describe, expect, it, vi } from 'vitest'

const uploadMock = vi.hoisted(() => vi.fn())
const toastError = vi.hoisted(() => vi.fn())

vi.mock('frappe-ui', () => ({
	FileUploadHandler: class {
		upload = uploadMock
	},
	toast: { error: toastError },
}))

// Compression has its own suite; here it only has to be on the upload path.
vi.mock('@/utils/compressImage', () => ({
	compressImage: vi.fn(
		async (file: File) =>
			new File(['small'], file.name.replace(/\.png$/, '.webp'), {
				type: 'image/webp',
			})
	),
}))

import { LessonImage } from '@/utils/lessonImage'
import { lessonUploadArgs, validateLessonFile } from '@/utils/lessonUpload'

const flush = async () => {
	for (let i = 0; i < 5; i++) await Promise.resolve()
	await new Promise((resolve) => setTimeout(resolve, 0))
}

// The slice of the EditorJS API the block touches, holding one block: ours.
const mountBlock = (config: Record<string, unknown> = {}) => {
	const holder = document.createElement('div')
	const api = {
		styles: { block: 'cdx-block', loader: 'cdx-loader', input: 'cdx-input' },
		blocks: {
			getCurrentBlockIndex: () => 0,
			getBlocksCount: () => 1,
			getBlockByIndex: () => ({ holder }),
			delete: vi.fn(),
		},
	}
	const block: any = new (LessonImage as any)({
		data: {},
		config,
		api,
		readOnly: false,
	})
	holder.appendChild(block.render())
	return { block, api }
}

const png = () =>
	new File(['x'.repeat(2000)], 'diagram.png', { type: 'image/png' })

;(globalThis as any).__ = (s: string) => s

beforeEach(() => {
	uploadMock.mockReset()
	toastError.mockReset()
})

describe('LessonImage: a pasted or dropped image file', () => {
	it('is uploaded, and the block stores the file URL rather than base64', async () => {
		// SimpleImage inlined the file as a data URL in the lesson's content JSON,
		// a 64 KB TEXT column, so one ordinary image made the lesson unsaveable.
		uploadMock.mockResolvedValue({ file_url: '/private/files/diagram.webp' })
		const { block } = mountBlock({ docname: 'LESSON-1', fieldname: 'content' })

		block.onPaste({ type: 'file', detail: { file: png() } })
		await flush()

		expect(block.data.url).toBe('/private/files/diagram.webp')
		expect(JSON.stringify(block.data)).not.toContain('data:')
	})

	it('compresses first and attaches the upload to the lesson', async () => {
		uploadMock.mockResolvedValue({ file_url: '/files/diagram.webp' })
		const { block } = mountBlock({ docname: 'LESSON-1', fieldname: 'content' })

		block.onPaste({ type: 'file', detail: { file: png() } })
		await flush()

		const [file, args] = uploadMock.mock.calls[0]
		expect(file.type).toBe('image/webp')
		expect(args).toEqual({
			private: false,
			doctype: 'Course Lesson',
			docname: 'LESSON-1',
			fieldname: 'content',
		})
	})

	it('removes the block and says so when the upload fails', async () => {
		uploadMock.mockRejectedValue(new Error('File too large'))
		const { block, api } = mountBlock()

		block.onPaste({ type: 'file', detail: { file: png() } })
		await flush()

		expect(toastError).toHaveBeenCalledWith('File too large')
		expect(api.blocks.delete).toHaveBeenCalledWith(0)
		expect(block.data.url).toBe('')
	})
})

describe('LessonImage: other pastes', () => {
	it('uploads an <img> whose pixels are inline instead of storing them', async () => {
		uploadMock.mockResolvedValue({
			file_url: '/private/files/pasted-image.png',
		})
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => ({
				blob: async () => new Blob(['x'], { type: 'image/png' }),
			}))
		)
		const { block } = mountBlock()

		block.onPaste({
			type: 'tag',
			detail: { data: { src: 'data:image/png;base64,AAAA' } },
		})
		await flush()
		vi.unstubAllGlobals()

		expect(uploadMock).toHaveBeenCalledTimes(1)
		expect(block.data.url).toBe('/private/files/pasted-image.png')
	})

	it('keeps a pasted image URL as it is, without uploading', async () => {
		const { block } = mountBlock()

		block.onPaste({
			type: 'pattern',
			detail: { data: 'https://example.com/photo.webp' },
		})
		await flush()

		expect(uploadMock).not.toHaveBeenCalled()
		expect(block.data.url).toBe('https://example.com/photo.webp')
	})
})

describe('LessonImage: save', () => {
	const contentFor = (src: string) => {
		const content = document.createElement('div')
		const img = document.createElement('img')
		img.src = src
		content.appendChild(img)
		const caption = document.createElement('div')
		caption.className = 'cdx-input'
		content.appendChild(caption)
		return content
	}

	it('stores an uploaded file as the path it was given, unencoded', async () => {
		// img.src comes back absolute and percent-encoded. The server matches a
		// private file to its lesson by finding file_url in the content, so the
		// stored value has to be the file_url itself.
		uploadMock.mockResolvedValue({ file_url: '/private/files/my diagram.webp' })
		const { block } = mountBlock()
		block.onPaste({ type: 'file', detail: { file: png() } })
		await flush()

		const saved = block.save(
			contentFor(`${window.location.origin}/private/files/my%20diagram.webp`)
		)

		expect(saved.url).toBe('/private/files/my diagram.webp')
	})

	it('leaves an external image URL untouched', () => {
		const { block } = mountBlock()
		block.onPaste({
			type: 'pattern',
			detail: { data: 'https://example.com/photo.webp' },
		})

		expect(block.save(contentFor('https://example.com/photo.webp')).url).toBe(
			'https://example.com/photo.webp'
		)
	})
})

describe('LessonImage: validate', () => {
	it('keeps a block that has an image and drops one that does not', () => {
		// Autosave can run while the upload is still in flight; an empty image
		// block saved then would render as a spinner that never resolves.
		const { block } = mountBlock()
		expect(block.validate({ url: '/private/files/diagram.webp' })).toBe(true)
		expect(block.validate({ url: '' })).toBe(false)
		expect(block.validate({ url: '   ' })).toBe(false)
	})
})

describe('lesson uploads', () => {
	it.each([
		'photo.webp',
		'photo.WEBP',
		'a.png',
		'a.jpg',
		'a.jpeg',
		'v.mp4',
		'd.pdf',
	])('accepts %s', (name) => {
		expect(validateLessonFile({ name })).toBeUndefined()
	})

	it.each(['script.svg', 'notes.txt', 'archive.zip', 'noextension'])(
		'refuses %s',
		(name) => {
			expect(validateLessonFile({ name })).toBeTypeOf('string')
		}
	)

	it('uploads publicly, and unattached until the lesson exists', () => {
		// A private lesson file loads only for its uploader and Administrator
		// wherever the stored URL is used as it is, the lesson editor first.
		expect(lessonUploadArgs({ docname: null, fieldname: 'content' })).toEqual({
			private: false,
		})
		expect(lessonUploadArgs(undefined)).toEqual({ private: false })
	})

	it('keeps a file added to the instructor notes private', () => {
		// Students are never sent that field, so its files stay behind the gate.
		expect(
			lessonUploadArgs({
				docname: 'LESSON-1',
				fieldname: 'instructor_content',
			})
		).toEqual({
			private: true,
			doctype: 'Course Lesson',
			docname: 'LESSON-1',
			fieldname: 'instructor_content',
		})
	})
})
