from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.test import TestCase
from django.urls import reverse
from chessclubs.forms import TournamentForm
from django.utils import timezone

class TournamentViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_officer(self.user2)
        self.client.login(email=self.user2.email, password='Password123')
        self.url = reverse('create_tournament', kwargs={'club_name': self.club.name})
        self.data = {'name': 'y'*40, 'location': 'x'*40, 'capacity':20, 'deadline':(timezone.now()+timezone.timedelta(days=1))}

    def test_view_create_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/create_tournament/')

    def test_get_create_tournament(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TournamentForm))
        self.assertFalse(form.is_bound)




    def test_successful_new_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        tournament_count_before = Tournament.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before + 1)
        new_tournament = Tournament.objects.last()
        self.assertEqual(self.user, new_tournament.organiser)
        response_url = reverse('landing_page')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_unsuccessful_new_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before)

    def test_cannot_create_tournament_for_other_user(self):
        self.client.login(email=self.user.email, password='Password123')
        other_user = User.objects.get(email='janedoe@example.org')
        self.data['organiser'] = other_user.id
        tournament_count_before = Tournament.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before + 1)
        new_tournament = Tournament.objects.last()
        self.assertEqual(self.user, new_tournament.organiser)




