from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart_page, name="cart_page"),
    # API endpoints for AJAX cart
    path("api/", views.CartDetailAPI.as_view(), name="api_cart_detail"),
    path(
        "api/add/<int:product_id>/",
        views.CartAddItemAPI.as_view(),
        name="api_cart_add",
    ),
    path(
        "api/remove/<int:item_id>/",
        views.CartRemoveItemAPI.as_view(),
        name="api_cart_remove",
    ),
    path(
        "api/update/<int:item_id>/",
        views.CartUpdateItemAPI.as_view(),
        name="api_cart_update",
    ),
]

