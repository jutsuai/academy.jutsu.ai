import frappe
from frappe import _
from frappe.utils import format_date, getdate, nowdate

from lms.lms.utils import get_lms_route

no_cache = 1


def get_context(context):
	"""The page a certificate's QR code opens.

	Public on purpose. The certificate PDF itself needs a login, so someone handed a
	certificate had no way to check it; this answers the one question they have (is
	this genuine, and whose is it) from the certificate ID alone. IDs are random
	hashes, so holding one means having been shown the certificate.
	"""
	context.no_cache = 1
	context.brand_name = frappe.db.get_single_value("Website Settings", "app_name") or "Frappe Learning"
	context.favicon = (
		frappe.db.get_single_value("Website Settings", "favicon") or "/assets/lms/frontend/favicon.png"
	)
	context.home_url = get_lms_route()

	certificate_id = frappe.form_dict.get("certificate_id")
	context.certificate_id = certificate_id if isinstance(certificate_id, str) else ""
	context.certificate = get_certificate(context.certificate_id)

	if context.certificate:
		context.title = _("Certificate of {0}").format(context.certificate.member_name)
	else:
		context.title = _("Certificate not found")
		context.http_status_code = 404


def get_certificate(certificate_id: str):
	# Names are 10-character hashes; anything longer is not worth a query.
	if not certificate_id or len(certificate_id) > 140:
		return None

	certificate = frappe.db.get_value(
		"LMS Certificate",
		certificate_id,
		["name", "member", "member_name", "course", "batch_title", "issue_date", "expiry_date"],
		as_dict=True,
	)
	if not certificate:
		return None

	course_title = (
		frappe.db.get_value("LMS Course", certificate.course, "title") if certificate.course else None
	)
	expired = bool(certificate.expiry_date and getdate(certificate.expiry_date) < getdate(nowdate()))

	# Only what is printed on the certificate. Never the member's email address,
	# which is what `member` holds.
	return frappe._dict(
		name=certificate.name,
		member_name=frappe.db.get_value("User", certificate.member, "full_name") or certificate.member_name,
		award_title=course_title or certificate.batch_title,
		is_course=bool(course_title),
		batch_title=certificate.batch_title if course_title else None,
		course_url=get_lms_route(f"courses/{certificate.course}") if certificate.course else None,
		issue_date=format_date(certificate.issue_date, "long") if certificate.issue_date else None,
		expiry_date=format_date(certificate.expiry_date, "long") if certificate.expiry_date else None,
		expired=expired,
	)
