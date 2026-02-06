from django.urls import path

from . import views

urlpatterns = [
    # HTML pages
    path("", views.product_list_page, name="product_list"),
    path("<slug:slug>/", views.product_detail_page, name="product_detail"),
    # API endpoints
    path("api/list/", views.ProductListAPI.as_view(), name="api_product_list"),
    path(
        "api/<slug:slug>/",
        views.ProductDetailAPI.as_view(),
        name="api_product_detail",
    ),
]

