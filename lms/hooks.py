import frappe

from . import __version__ as app_version

app_name = "frappe_lms"
app_title = "Learning"
app_publisher = "Frappe"
app_description = "Open Source Learning Management System built with Frappe Framework"
app_icon_url = "/assets/lms/images/lms-logo.png"
app_icon_title = "Learning"
app_icon_route = "/lms"
app_color = "grey"
app_email = "jannat@frappe.io"
app_license = "AGPL"
required_apps = ["frappe/payments"]


def get_lms_path():
	"""The path the SPA is mounted at, without slashes.

	An empty string is meaningful: it means the site root (`"lms_path": ""` in
	site_config.json), which is why the check below is an explicit `is not None`
	rather than a truthiness test — `or "lms"` would silently turn the root
	setting back into a /lms prefix.
	"""
	path = "lms"
	if frappe.conf:
		configured = frappe.conf.get("lms_path")
		if configured is not None:
			path = configured
	return path.strip("/")


def is_lms_at_root():
	"""True when the SPA owns the site root rather than a /lms prefix."""
	return get_lms_path() == ""


# The app's top-level route segments, mirroring frontend/src/routes.js.
#
# Only used in root mode. Frappe has to be told which first segments belong to
# the SPA, because the obvious `/<path:app_path>` catch-all would also swallow
# /login, /app, /api and every other Frappe route — the app would work and
# everything around it would break.
LMS_ROUTE_SEGMENTS = (
	"assignment-submission",
	"assignment-submissions",
	"assignments",
	"batches",
	"billing",
	"certified-participants",
	"courses",
	"data-import",
	"design-system",
	"job-opening",
	"job-openings",
	"persona",
	"programming-exercises",
	"programs",
	"quiz",
	"quiz-submission",
	"quiz-submissions",
	"quizzes",
	"settings",
	"statistics",
	"user",
	"you",
)


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lms/css/lms.css"
# app_include_js = "/assets/lms/js/lms.js"

# include js, css files in header of web template
# The Jutsu theme for Frappe's own server-rendered pages — login, sign-up,
# forgot-password, the website shell. Those pages are rendered by Frappe's
# website bundle, not by the SPA, so nothing the app imports reaches them and
# /login stayed light while the rest of the product went dark. They do use the
# same espresso token names, so re-declaring the variables carries the theme
# across. Generated from the app's own token file — see
# frontend/scripts/build-web-theme.mjs; `yarn build` regenerates it.
def _jutsu_web_css():
	"""The web theme's URL, carrying a content hash as a cache buster.

	The file is a plain static asset under `public/`, not a Frappe bundle, so
	nothing appends a version to it and a browser would hold the first copy it
	ever fetched — which is exactly what happened while this was being built:
	the file on disk was correct and the page kept rendering the old one.
	Hashing the contents means the URL changes only when the theme does.

	Falls back to the bare path if the file cannot be read, so a missing or
	unreadable theme degrades to "no cache busting" rather than to a broken
	<link> or an exception during hook evaluation.
	"""
	import hashlib
	import os

	path = os.path.join(os.path.dirname(__file__), "public", "css", "jutsu-web.css")
	try:
		with open(path, "rb") as handle:
			digest = hashlib.sha1(handle.read()).hexdigest()[:10]
	except OSError:
		return "/assets/lms/css/jutsu-web.css"
	return f"/assets/lms/css/jutsu-web.css?v={digest}"


web_include_css = [_jutsu_web_css()]
web_include_js = []

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# The LMS *is* the product here, so the site root serves the app rather than a
# Frappe website home page. Deep links keep working through the existing
# `/{lms_path}/...` rules below; this only decides what "/" renders.
home_page = "_lms"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "lms.install.before_install"
after_install = "lms.install.after_install"
after_sync = "lms.install.after_sync"
before_uninstall = "lms.install.before_uninstall"
setup_wizard_complete = "lms.demo.demo_data.create_demo_data"
after_migrate = [
	"lms.sqlite.build_index_in_background",
	"lms.lms.doctype.lms_payment.lms_payment.add_unique_payment_id_constraint",
]

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"LMS Certificate": "lms.lms.doctype.lms_certificate.lms_certificate.get_permission_query_conditions",
	"LMS Live Class": "lms.lms.doctype.lms_live_class.lms_live_class.get_permission_query_conditions",
	"LMS Batch": "lms.lms.doctype.lms_batch.lms_batch.get_permission_query_conditions",
	"LMS Program": "lms.lms.doctype.lms_program.lms_program.get_permission_query_conditions",
	"Course Lesson": "lms.lms.doctype.course_lesson.course_lesson.get_permission_query_conditions",
}

has_permission = {
	"LMS Live Class": "lms.lms.doctype.lms_live_class.lms_live_class.has_permission",
	"LMS Batch": "lms.lms.doctype.lms_batch.lms_batch.has_permission",
	"LMS Program": "lms.lms.doctype.lms_program.lms_program.has_permission",
	"LMS Certificate": "lms.lms.doctype.lms_certificate.lms_certificate.has_permission",
	"Course Lesson": "lms.lms.doctype.course_lesson.course_lesson.has_permission",
	"File": "lms.lms.permissions.file_has_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Web Template": "lms.overrides.web_template.CustomWebTemplate",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_change": [
			"lms.lms.doctype.lms_badge.lms_badge.process_badges",
		]
	},
	"Discussion Reply": {
		"after_insert": "lms.lms.utils.handle_notifications",
		"validate": "lms.lms.utils.validate_discussion_reply",
	},
	"Notification Log": {"on_change": "lms.lms.utils.publish_notifications"},
	"User": {
		"validate": "lms.lms.user.validate_username_duplicates",
		"before_insert": "lms.lms.user.add_lms_student_role",
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"all": [
		"lms.sqlite.build_index_in_background",
	],
	"hourly": [
		"lms.lms.doctype.lms_certificate_request.lms_certificate_request.schedule_evals",
		"lms.lms.doctype.lms_course.lms_course.update_course_statistics",
		"lms.lms.doctype.lms_certificate_request.lms_certificate_request.mark_eval_as_completed",
		"lms.lms.doctype.lms_live_class.lms_live_class.update_attendance",
	],
	"daily": [
		"lms.job.doctype.job_opportunity.job_opportunity.update_job_openings",
		"lms.lms.doctype.lms_payment.lms_payment.send_payment_reminder",
		"lms.lms.doctype.lms_batch.lms_batch.send_batch_start_reminder",
		"lms.lms.doctype.lms_live_class.lms_live_class.send_live_class_reminder",
		"lms.lms.doctype.lms_course.lms_course.send_notification_for_published_courses",
		"lms.lms.doctype.course_lesson.course_lesson.rename_settled_untitled_lessons",
	],
}

fixtures = ["Custom Field", "Function", "Industry", "LMS Category"]

# Testing
# -------

# before_tests = "lms.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.search.get_names_for_mentions": "lms.lms.utils.get_names_for_mentions",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Add all simple route rules here
#
# Two shapes, chosen by `lms_path`:
#
#   prefixed (default, lms_path="lms")  one `<path:app_path>` rule under the
#       prefix — everything below /lms is the SPA's, nothing above it is.
#
#   root (lms_path="")  one rule PER top-level segment. A bare
#       `/<path:app_path>` would match /login, /app, /api and every other
#       Frappe route as well, so the SPA's segments are named explicitly.
#       `/` itself is served by `home_page` above, not by a rule.
website_route_rules = (
	[
		{"from_route": f"/{segment}", "to_route": "_lms"}
		for segment in LMS_ROUTE_SEGMENTS
	]
	+ [
		{"from_route": f"/{segment}/<path:app_path>", "to_route": "_lms"}
		for segment in LMS_ROUTE_SEGMENTS
	]
	if is_lms_at_root()
	else [
		{"from_route": f"/{get_lms_path()}/<path:app_path>", "to_route": "_lms"},
		{"from_route": f"/{get_lms_path()}", "to_route": "_lms"},
	]
) + [
	{
		"from_route": "/courses/<course_name>/<certificate_id>",
		"to_route": "certificate",
	},
]

# The prefix redirects exist to move legacy top-level URLs under /lms. At the
# root they would point each URL at itself, so only the genuine rename survives.
website_redirects = [
	{"source": "/update-profile", "target": "/edit-profile"},
] + ([] if is_lms_at_root() else [
	{"source": "/courses", "target": f"/{get_lms_path()}/courses"},
	{
		"source": r"^/courses/.*$",
		"target": f"/{get_lms_path()}/courses",
	},
	{"source": "/batches", "target": f"/{get_lms_path()}/batches"},
	{
		"source": r"/batches/(.*)",
		"target": f"/{get_lms_path()}/batches",
		"match_with_query_string": True,
	},
	{"source": "/job-openings", "target": f"/{get_lms_path()}/job-openings"},
	{
		"source": r"/job-openings/(.*)",
		"target": f"/{get_lms_path()}/job-openings",
		"match_with_query_string": True,
	},
	{"source": "/statistics", "target": f"/{get_lms_path()}/statistics"},
	{"source": "_lms", "target": f"/{get_lms_path()}"},
])

update_website_context = [
	"lms.widgets.update_website_context",
]

jinja = {
	"methods": [
		"lms.lms.utils.get_lesson_count",
		"lms.lms.utils.get_instructors",
		"lms.lms.utils.get_lesson_index",
		"lms.lms.utils.get_lesson_url",
		"lms.lms.utils.get_lms_route",
		"lms.lms.utils.is_instructor",
		"lms.lms.utils.get_palette",
	],
	"filters": [],
}

extend_bootinfo = [
	"lms.lms.utils.extend_bootinfo",
]
## Specify the additional tabs to be included in the user profile page.
## Each entry must be a subclass of lms.lms.plugins.ProfileTab
# profile_tabs = []

## Specify the extension to be used to control what scripts and stylesheets
## to be included in lesson pages. The specified value must be be a
## subclass of lms.plugins.PageExtension
# lms_lesson_page_extension = None

# lms_lesson_page_extensions = [
# 	"lms.plugins.LiveCodeExtension"
# ]

has_website_permission = {
	"LMS Certificate Evaluation": "lms.lms.doctype.lms_certificate_evaluation.lms_certificate_evaluation.has_website_permission",
	"LMS Certificate": "lms.lms.doctype.lms_certificate.lms_certificate.has_website_permission",
}

## Markdown Macros for Lessons
lms_markdown_macro_renderers = {
	"Exercise": "lms.plugins.exercise_renderer",
	"Quiz": "lms.plugins.quiz_renderer",
	"YouTubeVideo": "lms.plugins.youtube_video_renderer",
	"Video": "lms.plugins.video_renderer",
	"Assignment": "lms.plugins.assignment_renderer",
	"Embed": "lms.plugins.embed_renderer",
	"Audio": "lms.plugins.audio_renderer",
	"PDF": "lms.plugins.pdf_renderer",
}

page_renderer = [
	"lms.page_renderers.SCORMRenderer",
]

# set this to "/" to have profiles on the top-level
profile_url_prefix = "/users/"

signup_form_template = "lms.plugins.show_custom_signup"

on_login = "lms.lms.user.on_login"

get_site_info = "lms.activation.get_site_info"

add_to_apps_screen = [
	{
		"name": "lms",
		"logo": "/assets/lms/frontend/learning.svg",
		"title": "Learning",
		"route": f"/{get_lms_path()}",
		"has_permission": "lms.lms.api.check_app_permission",
	}
]

sqlite_search = ["lms.sqlite.LearningSearch"]
auth_hooks = ["lms.auth.authenticate"]
require_type_annotated_api_methods = True

# === Raven membership provider ===
# Hook contract + admin setup: ../raven-membership-provider.md
# TODO: that page is an interim capture. Publish it at docs.frappe.io/learning
# (specs/extensibility.md: "A hook isn't shipped until the docs exist") and delete it.
# LMS contributes its rule types + evaluator to the standalone `raven_integration`
# app via the `raven_membership_providers` hook. See lms/raven_provider.py.
raven_membership_providers = ["lms.raven_provider.get_provider"]

# Settings > Integrations > Raven sits inside the Settings modal, which is open to
# any Moderator, so the endpoints behind it have to be too. raven_integration gates
# on System Manager plus whatever this hook names, and grants the named roles the
# permissions its own doctypes need on install/migrate.
raven_integration_manager_roles = ["Moderator"]
