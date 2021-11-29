from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next
from chessclubs.tests.helpers import ClubGroupTester
from notifications.models import Notification
from notifications.signals import notify
from django.test import TestCase
from django.urls import reverse

class ApplicationViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.club.members.add(self.user)
        self.client.login(email=self.user.email, password='Password123')
        self.url = reverse('view_applications', kwargs={'club_name': self.club.name})

    def test_view_application_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/view_applications/')
