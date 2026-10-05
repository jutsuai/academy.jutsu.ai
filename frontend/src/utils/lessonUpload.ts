// The upload arguments every file added to a lesson body shares, whichever
// editor block uploads it.

export type LessonUploadContext = {
	docname?: string | null
	fieldname?: string
}

type LessonUploadArgs = {
	private: boolean
	doctype?: 'Course Lesson'
	docname?: string
	fieldname?: string
}

// The lesson fields only the course's authors read. Their files stay private.
const INSTRUCTOR_FIELDS = ['instructor_content', 'instructor_notes']

// Lesson files are public. Frappe serves a private file only to its uploader
// and Administrator, so anyone else who met the stored URL as it is (the
// lesson editor loads it that way) saw a broken image.
//
// Attach to the lesson only once it exists: a null docname with doctype set
// makes the File doctype reject the upload.
export function lessonUploadArgs(
	context?: LessonUploadContext | null
): LessonUploadArgs {
	const args: LessonUploadArgs = {
		private: INSTRUCTOR_FIELDS.includes(context?.fieldname ?? ''),
	}
	const docname = context?.docname
	if (docname) {
		args.doctype = 'Course Lesson'
		args.docname = docname
		args.fieldname = context?.fieldname || 'content'
	}
	return args
}

// What the lesson Upload block accepts, by file extension.
const LESSON_FILE_EXTENSIONS = [
	'jpg',
	'jpeg',
	'png',
	'webp',
	'mp4',
	'mov',
	'mp3',
	'pdf',
]

/** The message to show when a file is refused; undefined when it is allowed. */
export function validateLessonFile(file: { name: string }): string | undefined {
	const extension = file.name.split('.').pop()?.toLowerCase() ?? ''
	if (!LESSON_FILE_EXTENSIONS.includes(extension)) {
		return 'Only image, video, audio and PDF files are allowed.'
	}
}
