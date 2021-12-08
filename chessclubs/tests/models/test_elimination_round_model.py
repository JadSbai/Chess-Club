import math

from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, EliminationRounds
from chessclubs.tests.helpers import ClubGroupTester


class EliminationRoundTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_elimination_round.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email="janedoe@example.org")
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.elimination_round = EliminationRounds.objects.get(pk=1)
        self.group_tester = ClubGroupTester(self.club)
        self.dic = {2: "Final", 3: "Semi-Final", 4: "Semi-Final", 5: "Quarter-Final", 6: "Quarter-Final",
                    7: "Quarter-Final",
                    8: "Quarter-Final", 9: "Eighth-Final", 10: "Eighth-Final", 11: "Eighth-Final", 12: "Eighth-Final",
                    13: "Eighth-Final", 14: "Eighth-Final", 15: "Eighth-Final", 16: "Eighth-Final"}

    def test_get_matches_schedule(self):
        for count in range(2, 17):
            participants = self._create_test_players(count)
            self.elimination_round.add_players(participants)
            self.elimination_round.set_phase()
            self.elimination_round.generate_schedule()
            number_of_matches = self.elimination_round.schedule.all().count()
            self.assertEqual(number_of_matches, math.floor(count/2))
            self._assert_elimination_round_is_valid()
            self.elimination_round.remove_all_players()

    def _create_test_players(self, user_count=10):
        participants = []
        for user_id in range(user_count):
            user = User.objects.create_user(
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
                chess_experience=f'Standard{user_id}',
                personal_statement=f'My name is {user_id}',
            )
            self.club.add_member(user)
            self.tournament.add_participant(user)
            participants.append(user)
        return participants

    def test_phase_must_be_among_choices(self):
        self.elimination_round.phase = "bad_choice"
        self._assert_elimination_round_is_invalid()

    def test_phase_cannot_be_blank(self):
        self.elimination_round.phase = ''
        self._assert_elimination_round_is_invalid()

    def test_set_phase_is_accurate(self):
        for count in range(2, 17):
            participants = self._create_test_players(count)
            self.elimination_round.add_players(participants)
            self.elimination_round.set_phase()
            self.assertEqual(self.dic[count], self.elimination_round.phase)
            self.elimination_round.remove_all_players()

    def test_remove_match_from_schedule(self):
        participants = self._create_test_players(2)
        self.elimination_round.add_players(participants)
        self.elimination_round.set_phase()
        self.elimination_round.generate_schedule()
        first_match = self.elimination_round.schedule.all()[0]
        before = self.elimination_round.schedule.all().count()
        self.elimination_round.enter_winner(player=participants[0], match=first_match)
        after = self.elimination_round.schedule.all().count()
        self.assertEqual(before - 1, after)

    def _assert_elimination_round_is_valid(self):
        try:
            self.elimination_round.full_clean()
        except ValidationError:
            self.fail('Test elimination round should be valid')

    def _assert_elimination_round_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.elimination_round.full_clean()
