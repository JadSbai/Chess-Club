"""Tests of accept."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next

class AcceptViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('accept')

    def test_accept_url(self):
        self.assertEqual(self.url, 'accept/<int:user_id>')

    def test_accept_and_become_member(self):


    def test_application_number_minus_one(self):


    def test_redirect_to_application_page(self):



    def test_notification_sent(self):

