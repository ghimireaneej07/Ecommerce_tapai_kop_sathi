from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkout_start, name="checkout_start"),
    path(
        "success/<str:order_number>/",
        views.order_success,
        name="order_success",
    ),
    path(
        "failure/<str:order_number>/",
        views.order_failure,
        name="order_failure",
    ),
    path("history/", views.order_history, name="order_history"),
]

