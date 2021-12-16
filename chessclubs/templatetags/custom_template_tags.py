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


@register.filter(name='pool_number')
def get_pool_number(pools_count, i):
    return pools_count - i

@register.simple_tag
def decrement(i):
    return i - 1

@register.simple_tag
def increment(i):
    return i + 1

@register.simple_tag
def past_tournaments(tournaments):
    past = []
    for tournament in tournaments:
        if tournament.has_finished():
            past.append(tournament)
    return past

@register.simple_tag
def current_tournaments(tournaments):
    current = []
    for tournament in tournaments:
        if tournament.has_started() and not tournament.has_finished():
            current.append(tournament)
    return current

@register.simple_tag
def future_tournaments(tournaments):
    future = []
    for tournament in tournaments:
        if not tournament.has_started():
            future.append(tournament)
    return future

@register.simple_tag
def lengthof(some_list):
    return len(some_list)