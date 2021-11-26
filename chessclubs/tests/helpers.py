from django.urls import reverse
from chessclubs.groups import set_up_app_groups


def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()


class GroupTester:

    def __init__(self):
        self.groups = set_up_app_groups()

    def make_applicant(self, user):
        user.groups.clear()
        user.groups.add(self.groups["applicants"])

    def make_denied_applicant(self, user):
        user.groups.clear()
        user.groups.add(self.groups["denied_applicants"])

    def make_member(self, user):
        user.groups.clear()
        user.groups.add(self.groups["members"])

    def make_officer(self, user):
        user.groups.clear()
        user.groups.add(self.groups["officers"])

    def make_owner(self, user):
        user.groups.clear()
        user.groups.add(self.groups["owner"])

    def make_authenticated_non_member(self, user):
        user.groups.clear()
        user.groups.add(self.groups["authenticated_non_member_users"])
