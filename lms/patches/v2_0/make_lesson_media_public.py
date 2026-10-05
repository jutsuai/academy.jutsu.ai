# Copyright (c) 2026, FOSS United and Contributors
# See license.txt

import filecmp
import os
import re
import shutil
from urllib.parse import quote, unquote

import frappe

# Text every learner reads: the lesson body, the quiz question, assignment brief
# and exercise statement embedded in it, and the course description. The files
# these point at were uploaded private, and Frappe serves a private file only to
# its uploader and Administrator, so anyone else who met the stored URL as it is
# (the lesson editor loads it that way, a question's HTML is sent that way) saw a
# broken image. The uploaders are public now; this moves what they left behind.
#
# Unlike make_public_images_public these fields hold a document (JSON, HTML or
# markdown) with file URLs inside it, not a bare URL, and one file is routinely
# uploaded into several lessons. So every File row sharing a URL moves together
# here, and each document is edited in place rather than overwritten.
PUBLIC_FIELDS = (
	("Course Lesson", "content"),
	("Course Lesson", "body"),
	("LMS Question", "question"),
	("LMS Assignment", "question"),
	("LMS Programming Exercise", "problem_statement"),
	("LMS Course", "description"),
)

# Not published for their own sake, but repointed when a file they share with a
# field above moves, so the move never leaves them on a URL that no longer exists.
FOLLOWING_FIELDS = (
	("Course Lesson", "instructor_content"),
	("Course Lesson", "instructor_notes"),
	("LMS Batch", "batch_details"),
	("LMS Batch", "batch_details_raw"),
)

# The lesson fields only the course's authors read (permissions.INSTRUCTOR_FIELDS).
INSTRUCTOR_FIELDS = ("instructor_content", "instructor_notes")

PRIVATE_PREFIX = "/private/files/"
PUBLIC_PREFIX = "/files/"

# The span rewrite_private_media treats as one private URL, stopped at a line end too.
PRIVATE_URL = re.compile(r"/private/files/[^\"'\\\n]+")


def execute():
	summary = {"published": 0, "left_alone": 0, "failed": 0}

	documents = read_documents(PUBLIC_FIELDS)
	to_publish = {url for text in documents.values() for url in PRIVATE_URL.findall(text)}
	if not to_publish:
		return summary
	documents.update(read_documents(FOLLOWING_FIELDS))

	# A URL is stored either as the File row has it or percent-encoded (the image
	# block used to save the browser's resolved src). Group both under the row's.
	spellings = {}
	for written in to_publish:
		url = written if frappe.db.exists("File", {"file_url": written}) else unquote(written)
		spellings.setdefault(url, set()).add(written)
	for text in documents.values():
		for written in PRIVATE_URL.findall(text):
			if written not in to_publish and unquote(written) in spellings:
				spellings[unquote(written)].add(written)

	for url, written_as in spellings.items():
		try:
			publish(url, written_as, documents, summary)
		except Exception:
			# One unreadable file must cost itself, not the rest of bench migrate.
			frappe.db.rollback()
			summary["failed"] += 1
			log(f"Could not make {url} public")

	frappe.logger("lms").info(f"make_lesson_media_public: {summary}")
	return summary


def read_documents(fields):
	"""{(doctype, name, fieldname): text} for every row holding a private URL."""
	documents = {}
	for doctype, fieldname in fields:
		if not frappe.db.exists("DocType", doctype) or not frappe.get_meta(doctype).get_field(fieldname):
			continue
		for row in frappe.get_all(
			doctype,
			filters={fieldname: ["like", f"%{PRIVATE_PREFIX}%"]},
			fields=["name", fieldname],
		):
			documents[(doctype, row.name, fieldname)] = row.get(fieldname)
	return documents


def publish(url, written_as, documents, summary):
	"""Move the file behind `url` to public/files and repoint what references it.

	Giving up always leaves the file, its File rows and the documents exactly as
	they were: the private URL keeps working through serve_resource.
	"""
	name = url[len(PRIVATE_PREFIX) :]
	files = frappe.get_all(
		"File",
		filters={"file_url": url},
		fields=["name", "attached_to_doctype", "attached_to_field"],
	)
	source = frappe.get_site_path("private", "files", name)
	if not files or os.path.basename(name) != name or not os.path.isfile(source):
		summary["failed"] += 1
		log(f"No File record or no file on disk for {url}")
		return

	if any(is_private_attachment(file) for file in files):
		summary["left_alone"] += 1
		return

	target = frappe.get_site_path("public", "files", name)
	if os.path.exists(target) and not filecmp.cmp(source, target, shallow=False):
		# A different public file already has this name.
		stem, extension = os.path.splitext(name)
		name = f"{stem}{frappe.generate_hash(length=6)}{extension}"
		target = frappe.get_site_path("public", "files", name)
	public_url = PUBLIC_PREFIX + name

	# Copy, commit, then delete: until the commit nothing points at the copy, and
	# after it nothing points at the original.
	copied = not os.path.exists(target)
	if copied:
		shutil.copy2(source, target)
	try:
		for file in files:
			frappe.db.set_value(
				"File", file.name, {"file_url": public_url, "is_private": 0}, update_modified=False
			)
		replacements = {
			written: public_url if written == url else quote(public_url) for written in written_as
		}
		repointed = {}
		for key, text in documents.items():
			new_text = PRIVATE_URL.sub(lambda m: replacements.get(m.group(0), m.group(0)), text)
			if new_text != text:
				doctype, docname, fieldname = key
				frappe.db.set_value(doctype, docname, fieldname, new_text, update_modified=False)
				repointed[key] = new_text
		frappe.db.commit()
	except Exception:
		if copied:
			os.remove(target)
		raise

	documents.update(repointed)
	summary["published"] += 1
	try:
		os.remove(source)
	except OSError:
		# Nothing references it any more; a leftover costs disk, not correctness.
		log(f"Published {url} but could not delete the private original")


def is_private_attachment(file):
	"""True if this row attaches the file to something that must stay private.

	Rows sharing a URL share the bytes, so publishing for a lesson would publish an
	assignment submission or instructor notes that hold the same upload.
	"""
	if not file.attached_to_doctype:
		return False
	if file.attached_to_doctype == "Course Lesson":
		return file.attached_to_field in INSTRUCTOR_FIELDS
	return file.attached_to_doctype not in {doctype for doctype, _ in PUBLIC_FIELDS}


def log(message):
	frappe.log_error(title="make_lesson_media_public", message=f"{message}\n\n{frappe.get_traceback()}")
