from django.conf import settings


def global_settings(request):
    """
    Expose a minimal set of global settings to templates.
    """
    return {
        "PROJECT_NAME": "Tapai Ko Sathi",
        "DEBUG": settings.DEBUG,
    }

