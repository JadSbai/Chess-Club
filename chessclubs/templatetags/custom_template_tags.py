from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='user_status')
def club_user_status(club, user):
    return club.user_status(user)


@register.filter(name='tournament_user_status')
def tournament_user_status(tournament, user):
    return tournament.user_status(user)


@register.simple_tag
def current_time():
    return timezone.now()
