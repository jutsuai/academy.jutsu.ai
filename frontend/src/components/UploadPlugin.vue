<template>
	<FileUploader
		:fileTypes="['image/*', 'video/*', 'audio/*', '.pdf']"
		:uploadArgs="uploadArgs"
		:validateFile="validateFile"
		@success="(data) => addFile(data)"
		ref="fileUploader"
		class="hide"
	/>
</template>
<script setup>
import { FileUploader, toast } from 'frappe-ui'
import { onMounted, ref, nextTick, computed } from 'vue'
import { lessonUploadArgs, validateLessonFile } from '@/utils/lessonUpload'

const fileUploader = ref(null)
const emit = defineEmits(['fileUploaded'])

const props = defineProps({
	onFileUploaded: {
		type: Function,
		required: true,
	},
	uploadContext: {
		type: Object,
		default: () => ({}),
	},
})

const uploadArgs = computed(() => lessonUploadArgs(props.uploadContext))

onMounted(async () => {
	await nextTick()
	const fileInput = fileUploader.value.$el.querySelector('input[type="file"]')
	if (fileInput) {
		fileInput.click()
	}
})

const addFile = (file) => {
	props.onFileUploaded({
		file_url: file.file_url,
		file_type: file.file_type,
	})
}

// The uploader is hidden (it only exists to open the file picker), so the
// message it would render is never seen: a refused file used to do nothing.
const validateFile = (file) => {
	const message = validateLessonFile(file)
	if (message) toast.error(__(message))
	return message
}

const isVideo = (type) => {
	return ['mov', 'mp4', 'avi', 'mkv', 'webm'].includes(type.toLowerCase())
}

const isAudio = (type) => {
	return ['mp3', 'wav', 'ogg'].includes(type.toLowerCase())
}
</script>
