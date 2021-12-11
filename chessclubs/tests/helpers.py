from django.urls import reverse
from chessclubs.models import User


def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()


class ClubGroupTester:
    """Helper class for allocating users to clubs groups"""

    def __init__(self, club):
        self.club = club
        self.club.assign_club_groups_permissions()
        if self.club.owner not in self.club.members.all():
            self.club.members.add(self.club.owner)

    def make_applicant(self, user):
        user.groups.clear()
        self.club.add_to_applicants_group(user)

    def make_denied_applicant(self, user):
        user.groups.clear()
        self.club.add_to_denied_applicants_group(user)

    def make_accepted_applicant(self, user):
        user.groups.clear()
        self.club.add_to_accepted_applicants_group(user)

    def make_member(self, user):
        if user not in self.club.members.all():
            self.club.members.add(user)
        user.groups.clear()
        self.club.add_to_members_group(user)

    def make_members(self, users):
        for user in users:
            self.make_member(user)

    def make_officer(self, user):
        if user not in self.club.members.all():
            self.club.members.add(user)
        user.groups.clear()
        self.club.add_to_officers_group(user)

    def make_authenticated_non_member(self, user):
        user.groups.clear()
        self.club.add_to_logged_in_non_members_group(user)


class TournamentGroupTester:
    """Helper class for allocating users to tournaments groups"""

    def __init__(self, tournament):
        self.tournament = tournament
        self.tournament.assign_tournament_permissions_and_groups()

    def make_participant(self, user):
        self.tournament.add_to_participants_group(user)

    def make_organiser(self, user):
        self.tournament.add_to_organisers_group(user)


def _create_test_players(user_count, club, tournament):
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
        club.add_member(user)
        new_player = tournament.add_participant(user)
        participants.append(new_player)
    return participants


def generate_pools_list(num, club, tournament, SPP):
    players = _create_test_players(num, club, tournament)
    SPP.add_players(players)
    pools_list = SPP.generate_schedule()
    return pools_list


def generate_elimination_matches_schedule(num, club, tournament, ER):
    participants = _create_test_players(num, club, tournament)
    ER.add_players(participants)
    ER.set_phase()
    schedule = ER.generate_schedule()
    return schedule


def get_right_number_of_pools():
    right_answers = {17: 5, 18: 5, 19: 5, 20: 5, 21: 6, 22: 6, 23: 6, 24: 6, 25: 7, 26: 7, 27: 7, 28: 7, 29: 8, 30: 8,
                     31: 8, 32: 8}
    return right_answers


def get_right_phase():
    dic = {2: "Final", 3: "Semi-Final", 4: "Semi-Final", 5: "Quarter-Final", 6: "Quarter-Final",
           7: "Quarter-Final",
           8: "Quarter-Final", 9: "Eighth-Final", 10: "Eighth-Final", 11: "Eighth-Final", 12: "Eighth-Final",
           13: "Eighth-Final", 14: "Eighth-Final", 15: "Eighth-Final", 16: "Eighth-Final"}
    return dic
