
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class ClubBackend(ModelBackend):
    """A backend that understands club-specific authorization and permissions"""

    def _get_user_club_permissions(self, user_obj, club):
        return Permission.objects.filter(
            club_permission__users=user_obj, club_permission__club=club
        )

    def _get_group_club_permissions(self, user_obj, club):
        user_groups_field = get_user_model()._meta.get_field("groups")
        user_groups_query = (
            "club_permission__groups__%s" % user_groups_field.related_query_name()
        )
        return Permission.objects.filter(
            **{user_groups_query: user_obj}, club_permission__club=club
        )

    def __get_club_permissions(self, user_obj, club, from_name):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        perm_cache_name = f"_{from_name}_project_{club.pk}_perm_cache"
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, "_get_%s_club_permissions" % from_name)(
                    user_obj, club
                )
            perms = perms.values_list("content_type__app_label", "codename").order_by()
            setattr(
                user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms}
            )
        return getattr(user_obj, perm_cache_name)

    def get_user_club_permissions(self, user_obj, club):
        return self.__get_club_permissions(user_obj, club, "user")

    def get_group_club_permissions(self, user_obj, club):
        return self.__get_club_permissions(user_obj, club, "group")

    def get_all_club_permissions(self, user_obj, club):
        return {
            *self.get_user_club_permissions(user_obj, club),
            *self.get_group_club_permissions(user_obj, club),
            *self.get_user_permissions(user_obj),
            *self.get_group_permissions(user_obj),
        }

    def has_club_perm(self, user_obj, perm, club):
        return perm in self.get_all_club_permissions(user_obj, club)


class TournamentBackend(ModelBackend):
    """A backend that understands tournament-specific authorization and permissions"""

    def _get_user_tournament_permissions(self, user_obj, tournament):
        return Permission.objects.filter(
            tournament_permission__users=user_obj, tournament_permission__tournament=tournament
        )

    def _get_group_tournament_permissions(self, user_obj, tournament):
        user_groups_field = get_user_model()._meta.get_field("groups")
        user_groups_query = (
            "tournament_permission__groups__%s" % user_groups_field.related_query_name()
        )
        return Permission.objects.filter(
            **{user_groups_query: user_obj}, tournament_permission__tournament=tournament
        )

    def __get_tournament_permissions(self, user_obj, tournament, from_name):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        perm_cache_name = f"_{from_name}_project_{tournament.pk}_perm_cache"
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, "_get_%s_tournament_permissions" % from_name)(
                    user_obj, tournament
                )
            perms = perms.values_list("content_type__app_label", "codename").order_by()
            setattr(
                user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms}
            )
        return getattr(user_obj, perm_cache_name)

    def get_user_tournament_permissions(self, user_obj, tournament):
        return self.__get_tournament_permissions(user_obj, tournament, "user")

    def get_group_tournament_permissions(self, user_obj, tournament):
        return self.__get_tournament_permissions(user_obj, tournament, "group")

    def get_all_tournament_permissions(self, user_obj, tournament):
        return {
            *self.get_user_tournament_permissions(user_obj, tournament),
            *self.get_group_tournament_permissions(user_obj, tournament),
            *self.get_user_permissions(user_obj),
            *self.get_group_permissions(user_obj),
        }

    def has_tournament_perm(self, user_obj, perm, tournament):
        return perm in self.get_all_tournament_permissions(user_obj, tournament)
