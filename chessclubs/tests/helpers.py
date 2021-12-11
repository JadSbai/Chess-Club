from django.urls import reverse


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
        # user.groups.clear()
        self.tournament.add_to_participants_group(user)

    def make_organiser(self, user):
        # user.groups.clear()
        self.tournament.add_to_organisers_group(user)
