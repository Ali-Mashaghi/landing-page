from .models import User


def site_profile(request):
    profile = None
    if request.user.is_authenticated:
        profile = (
            User.objects.filter(pk=request.user.pk, is_active=True)
            .prefetch_related('skills')
            .first()
        )
    return {'site_profile': profile}
