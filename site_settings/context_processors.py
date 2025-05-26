import jdatetime

from .models import SiteSetting


def global_context(request):
    try:
        settings = SiteSetting.objects.first()
    except SiteSetting.DoesNotExist:
        settings = None

    return {
        'site_settings': settings,
        'current_year': jdatetime.date.today().year,

    }
