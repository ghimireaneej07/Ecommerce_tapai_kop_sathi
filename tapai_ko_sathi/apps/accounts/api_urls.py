from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import api

urlpatterns = [
    path("register/", api.RegisterAPIView.as_view(), name="api_register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", api.MeAPIView.as_view(), name="api_me"),
]
