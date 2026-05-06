from django.core.exceptions import ObjectDoesNotExist


def user_profile(request):
    profile = None
    if getattr(request, 'user', None) and request.user.is_authenticated:
        try:
            profile = request.user.profile
        except ObjectDoesNotExist:
            profile = None

    return {
        'user_profile': profile,
    }
