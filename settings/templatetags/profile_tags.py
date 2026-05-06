from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


def _get_profile(user):
    if user is None:
        return None
    try:
        return user.profile
    except (AttributeError, ObjectDoesNotExist):
        return None


@register.filter
def profile_position(user, default='Staff'):
    profile = _get_profile(user)
    if profile is None:
        return default
    return profile.position or default


@register.filter
def profile_phone(user, default='—'):
    profile = _get_profile(user)
    if profile is None:
        return default
    return profile.phone or default


@register.filter
def profile_avatar_url(user, default=''):
    profile = _get_profile(user)
    if profile is None:
        return default
    if profile.avatar:
        try:
            return profile.avatar.url
        except Exception:
            return default
    return default
