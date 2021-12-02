from django import template

register = template.Library()


@register.filter(name='user_status')
def cut(club, user):
    return club.user_status(user)
