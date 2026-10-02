import SimpleImage from '@editorjs/simple-image'
import { FileUploadHandler, toast } from 'frappe-ui'
import { compressImage } from '@/utils/compressImage'
import { lessonUploadArgs } from '@/utils/lessonUpload'

// The lesson editor's image block.
//
// SimpleImage has no upload of its own: an image file pasted or dropped into
// the editor is read with FileReader and stored in the block as a base64 data
// URL, inside the lesson's content JSON. That field is a 64 KB TEXT column, so
// any image over about 48 KB made the whole lesson unsaveable ("The value of
// the field Content is too long"). This uploads the file instead and stores
// only its URL, which is also what lets the browser cache the image.
export class LessonImage extends SimpleImage {
	constructor(options) {
		super(options)
		// The same context the Upload block gets, so both upload the same way.
		this.uploadContext = options.config || {}
	}

	onPaste(event) {
		if (event.type === 'file') {
			this.uploadAndShow(event.detail.file)
			return
		}
		// An <img> copied out of a document or another page can carry its
		// pixels inline too, and would overflow the field the same way.
		const src = event.type === 'tag' ? event.detail.data?.src : null
		if (typeof src === 'string' && src.startsWith('data:image/')) {
			fileFromDataUrl(src).then(
				(file) => this.uploadAndShow(file),
				() => this.fail()
			)
			return
		}
		super.onPaste(event)
	}

	async uploadAndShow(file) {
		try {
			const uploaded = await new FileUploadHandler().upload(
				await compressImage(file),
				lessonUploadArgs(this.uploadContext)
			)
			this.data = { url: uploaded.file_url, caption: file.name }
		} catch (error) {
			this.fail(error)
		}
	}

	// A block with no image would sit on its loading spinner forever.
	fail(error) {
		toast.error(error?.message || __('The image could not be uploaded.'))
		const blocks = this.api.blocks
		for (let index = 0; index < blocks.getBlocksCount(); index++) {
			if (
				blocks
					.getBlockByIndex(index)
					?.holder?.contains(this.nodes.wrapper)
			) {
				blocks.delete(index)
				return
			}
		}
	}

	// SimpleImage saves a block with no image as readily as one with. Autosave
	// can run while an upload is still in flight, and a block whose upload
	// failed has nothing to show, so neither belongs in the lesson.
	validate(savedData) {
		return Boolean(savedData.url?.trim())
	}

	// SimpleImage saves img.src, which the browser has resolved: absolute, and
	// percent-encoded. Keep the URL the block was given instead. The server
	// finds a private file's lesson by looking for its file_url in the lesson
	// content, so "my%20diagram.webp" would not match "my diagram.webp", and
	// a path keeps the lesson independent of the host it was written on.
	save(blockContent) {
		const given = this.data.url
		const data = super.save(blockContent)
		if (given && new URL(given, window.location.href).href === data.url) {
			data.url = given
		}
		return data
	}
}

async function fileFromDataUrl(dataUrl) {
	const blob = await (await fetch(dataUrl)).blob()
	const extension = blob.type.split('/')[1]?.split('+')[0] || 'png'
	return new File([blob], `pasted-image.${extension}`, { type: blob.type })
}
