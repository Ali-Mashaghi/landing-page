from .models import User


def site_profile(request):
    profile = User.objects.filter(is_staff=True, is_active=True).order_by('id').first()
    return {'site_profile': profile}
