# Copyright (c) 2026, FOSS United and Contributors
# See license.txt

import re

import frappe
import pyqrcode
from frappe.utils import add_days, nowdate

from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import get_qr_code_path
from lms.www.verify_certificate import get_certificate

STUDENT = "verify-student@example.com"


class TestCertificateQRCode(BaseTestUtils):
	def test_path_redraws_the_code_it_was_built_from(self):
		# The print format draws this path as the certificate's QR code. Merging
		# runs into rectangles is where it could go wrong, and a code that is one
		# module off simply does not scan.
		url = "https://academy.example.com/verify/0kkrcotcso"
		expected = pyqrcode.create(url, error="M").code

		qr = get_qr_code_path(url)
		self.assertEqual(qr["size"], len(expected))

		drawn = [[0] * qr["size"] for _ in range(qr["size"])]
		for x, y, width in re.findall(r"M(\d+) (\d+)h(\d+)v1h-\d+z", qr["path"]):
			for column in range(int(x), int(x) + int(width)):
				drawn[int(y)][column] = 1
		self.assertEqual(drawn, expected)


class TestCertificateVerification(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self._create_user("frappe@example.com", "Frappe", "Admin", ["Moderator"])
		self.student = self._create_user(STUDENT, "Verity", "Student", ["LMS Student"])
		self.course = self._create_course(title="Verification Course")
		self._create_enrollment(STUDENT, self.course.name)
		self.certificate = self._create_certificate(self.course.name, STUDENT)

	def test_a_real_certificate_is_described(self):
		found = get_certificate(self.certificate.name)

		self.assertEqual(found.name, self.certificate.name)
		self.assertEqual(found.member_name, "Verity Student")
		self.assertEqual(found.award_title, "Verification Course")
		self.assertTrue(found.is_course)
		self.assertFalse(found.expired)

	def test_the_public_page_never_carries_the_member_email(self):
		# The page is open to anyone holding the ID, and `member` on the
		# certificate is the learner's email address.
		found = get_certificate(self.certificate.name)

		self.assertNotIn(STUDENT, [str(value) for value in found.values()])

	def test_an_unpublished_certificate_still_verifies(self):
		# `published` decides whether the PDF is public. Verification must not
		# depend on it, or every certificate issued with the default would fail.
		frappe.db.set_value("LMS Certificate", self.certificate.name, "published", 0)

		self.assertIsNotNone(get_certificate(self.certificate.name))

	def test_a_lapsed_certificate_is_reported_as_expired(self):
		frappe.db.set_value("LMS Certificate", self.certificate.name, "expiry_date", add_days(nowdate(), -1))

		self.assertTrue(get_certificate(self.certificate.name).expired)

	def test_a_certificate_valid_through_today_is_not_expired(self):
		frappe.db.set_value("LMS Certificate", self.certificate.name, "expiry_date", nowdate())

		self.assertFalse(get_certificate(self.certificate.name).expired)

	def test_unknown_or_malformed_ids_find_nothing(self):
		for certificate_id in ("", "no-such-certificate", "x" * 500):
			with self.subTest(certificate_id=certificate_id[:20]):
				self.assertIsNone(get_certificate(certificate_id))
