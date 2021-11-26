"""Tests of deny."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next
from chessclubs.tests.helpers import GroupTester
from chessclubs.groups import groups
from notifications.models import Notification
from notifications.signals import notify


class AcceptViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json'
                ]

    def setUp(self):
        self.officer = User.objects.get(email='johndoe@example.org')
        self.applicant = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester = GroupTester()
        self.group_tester.make_applicant(self.applicant)
        self.group_tester.make_officer(self.officer)
        self.url = reverse('deny', kwargs={'user_id': self.applicant.id})

    def test_deny_url(self):
        self.assertEqual(self.url, '/deny/% s' % self.applicant.id)

    def test_accept_and_become_denied_applicant(self):
        before_status = self.applicant.status()
        self.assertEqual(before_status, "applicant")
        self.client.get(self.url)
        self.assertEqual(self.applicant.status(), "denied_applicant")
        self.assertTrue(self.applicant.groups.filter(name="denied_applicants").exists())
        self.assertFalse(self.applicant.groups.filter(name="applicants").exists())

    def test_redirect_to_application_page(self):
        self.target_url = reverse('view_applications')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)

    def test_number_of_applications_decremented(self):
        before = groups["applicants"].user_set.count()
        self.client.get(self.url)
        self.assertEqual(groups["applicants"].user_set.count(), before - 1)

    def test_notification_sent(self):
        notifications = len(self.applicant.notifications.unread())
        self.client.get(self.url)
        last_notification = self.applicant.notifications.unread()[0].description
        self.assertEqual(len(self.applicant.notifications.unread()), notifications + 1)
        self.assertEqual(last_notification, "Your application has been denied")

    def test_acknowledged_button_is_displayed(self):
        self.client.get(self.url)
        self.client.login(email=self.applicant.email, password='Password123')
        applicant_profile = self.client.get(reverse('my_profile'))
        self.assertContains(applicant_profile, "Acknowledged", html=True)

    def test_notice_of_denial_is_displayed(self):
        self.client.get(self.url)
        self.client.login(email=self.applicant.email, password='Password123')
        applicant_profile = self.client.get(reverse('my_profile'))
        self.assertContains(applicant_profile, "Notice: Your application has been denied", html=True)