from django.urls import path

from . import views

urlpatterns = [
    path("init/<str:order_number>/", views.initiate_payment, name="initiate_payment"),
    path("api/status/<str:order_number>/", views.payment_status_api, name="payment_status_api"),
    path(
        "esewa/init/<str:order_number>/",
        views.esewa_init,
        name="esewa_init",
    ),
    path("esewa/success/", views.esewa_success, name="esewa_success"),
    path("esewa/failure/", views.esewa_failure, name="esewa_failure"),
    path("razorpay/callback/", views.razorpay_callback, name="razorpay_callback"),
    path("esewa/webhook/", views.esewa_webhook, name="esewa_webhook"),
    path("razorpay/webhook/", views.razorpay_webhook, name="razorpay_webhook"),
]

