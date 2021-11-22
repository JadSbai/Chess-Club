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
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email = 'janedoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester = GroupTester()
        self.group_tester.make_applicant(self.user2)
        self.group_tester.make_officer(self.user)
        self.url = reverse('deny', kwargs={'user_id': self.user2.id})


    def test_deny_and_not_become_member(self):
        response = self.client.get(self.url)
        self.assertFalse(self.user2.groups.filter(name="members").exists())
        #self.assertEqual(response,200)

    # def test_applicants_deleted(self):
    #     response = self.client.get(self.url)
    #     self.assertFalse(self.user2.groups.filter(name="applicants").exists())

    def test_redirect_to_application_page(self):
        self.target_url = reverse('view_applications')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)

    def test_number_of_applications_decremented(self):
        before = groups["applicants"].user_set.count()
        self.client.get(self.url)
        self.assertEqual(groups["applicants"].user_set.count(), before -1)

    def test_notification_sent(self):
        notifications = len(self.user2.notifications.unread())
        self.client.get(self.url)
        last_notification = self.user2.notifications.unread()[0].description
        self.assertEqual(len(self.user2.notifications.unread()), notifications+1)
        self.assertEqual(last_notification, "Your application has been denied")