from unittest.mock import patch

import frappe
from frappe.tests import UnitTestCase
from werkzeug.exceptions import HTTPException
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from lms.lms.user import redirect_website_users_to_lms


class TestRedirectWebsiteUsersToLMS(UnitTestCase):
	def redirect_for(self, path, user="student@example.com", user_type="Website User", method="GET", **form):
		"""Where the hook sends this request, or None when it lets it through."""
		request = Request(EnvironBuilder(path=path, method=method).get_environ())
		session = frappe._dict(user=user, data=frappe._dict(user_type=user_type))
		with patch.multiple(frappe, request=request, form_dict=frappe._dict(form), session=session):
			try:
				redirect_website_users_to_lms()
			except HTTPException as e:
				response = e.get_response()
				self.assertEqual(response.status_code, 302)
				return response.headers["Location"]
		return None

	def test_sends_website_users_from_dead_ends_to_the_lms(self):
		for path in ("/", "/desk", "/desk/", "/desk/learning", "/app", "/app/lms-course/x", "/apps"):
			with self.subTest(path=path):
				self.assertEqual(self.redirect_for(path), "/lms")

	def test_leaves_other_paths_alone(self):
		for path in (
			"/lms",
			"/lms/courses",
			"/me",
			"/login",
			"/update-password",
			"/desktop",
			"/applications",
			"/api/method/ping",
		):
			with self.subTest(path=path):
				self.assertIsNone(self.redirect_for(path))

	def test_leaves_desk_users_and_guests_alone(self):
		for path in ("/", "/desk"):
			with self.subTest(path=path):
				self.assertIsNone(self.redirect_for(path, user="Administrator", user_type="System User"))
				self.assertIsNone(self.redirect_for(path, user="Guest", user_type=None))

	def test_only_redirects_page_loads(self):
		self.assertIsNone(self.redirect_for("/", method="POST"))
		self.assertIsNone(self.redirect_for("/", cmd="frappe.auth.get_logged_user"))

	def test_follows_a_custom_lms_path(self):
		with patch.dict(frappe.conf, {"lms_path": "academy"}):
			self.assertEqual(self.redirect_for("/"), "/academy")
