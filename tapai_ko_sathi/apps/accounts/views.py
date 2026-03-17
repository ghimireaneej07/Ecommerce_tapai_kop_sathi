from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from django.http import HttpRequest, HttpResponse,  HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django.core.mail import send_mail

from .forms import LoginForm, ProfileForm, SignupForm
from .models import User
from .tokens import email_verification_token
from .utils import send_verification_email
from tapai_ko_sathi.apps.cart.utils import attach_cart_to_user


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        send_verification_email(self.request, user)
        messages.success(
            self.request,
            "Account created successfully. Please check your email to verify your address.",
        )
        login(self.request, user)
        attach_cart_to_user(self.request, user)
        return redirect(self.success_url)


class CustomLoginView(BaseLoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        # We need to call attach_cart_to_user after login
        response = super().form_valid(form)
        attach_cart_to_user(self.request, self.request.user)
        messages.success(self.request, "Welcome back!")
        return response

    def get_success_url(self):
        return self.request.GET.get("next") or reverse("dashboard")


class CustomLogoutView(BaseLogoutView):
    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None

        if user is not None and email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            messages.success(request, "Your email has been verified successfully.")
            return redirect("dashboard")

        messages.error(request, "Verification link is invalid or has expired.")
        return redirect("login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        display_name = user.first_name or user.username or user.email
        context["display_name"] = display_name
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


