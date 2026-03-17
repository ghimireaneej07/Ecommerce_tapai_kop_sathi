from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from tapai_ko_sathi.core import views as core_views
from tapai_ko_sathi.core import seo as core_seo

urlpatterns = [
    path("", core_views.home, name="home"),
    path("robots.txt", core_seo.robots_txt, name="robots_txt"),
    path("sitemap.xml", core_seo.sitemap_xml, name="sitemap_xml"),
    path("healthz/", core_views.health_check, name="health_check"),
    path("accounts/", include("tapai_ko_sathi.apps.accounts.urls")),
    path("api/accounts/", include("tapai_ko_sathi.apps.accounts.api_urls")),
    path("products/", include("tapai_ko_sathi.apps.products.urls")),
    path("cart/", include("tapai_ko_sathi.apps.cart.urls")),
    path("api/cart/", include("tapai_ko_sathi.apps.cart.api_urls")),
    path("orders/", include("tapai_ko_sathi.apps.orders.urls")),
    path("api/orders/", include("tapai_ko_sathi.apps.orders.api_urls")),
    path("payments/", include("tapai_ko_sathi.apps.payments.urls")),
    path("api/payments/", include("tapai_ko_sathi.apps.payments.api_urls")),
    path("adminpanel/", include("tapai_ko_sathi.apps.adminpanel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

