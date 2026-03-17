from django.conf import settings


def global_settings(request):
    """
    Expose a minimal set of global settings to templates.
    """
    context = {
        "PROJECT_NAME": "Tapai Ko Sathi",
        "DEBUG": settings.DEBUG,
    }

    try:
        from tapai_ko_sathi.apps.products.models import Category

        context["NAV_CATEGORIES"] = Category.objects.filter(is_active=True).order_by("name")
    except Exception:
        context["NAV_CATEGORIES"] = []

    return context

