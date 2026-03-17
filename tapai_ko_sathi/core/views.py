from django.shortcuts import render
from django.http import HttpResponse

from tapai_ko_sathi.apps.products.models import Product

def home(request):
    """
    Landing page highlighting the Tapai Ko Sathi product and related items.
    """
    featured_products = Product.objects.filter(is_active=True).order_by("-created_at")[
        :4
    ]
    return render(
        request,
        "core/home.html",
        {"featured_products": featured_products},
    )


def health_check(request):
    """Simple health-check endpoint used by load balancers and local checks."""
    return HttpResponse("ok")

