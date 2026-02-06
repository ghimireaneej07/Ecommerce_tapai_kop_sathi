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
from tapai_ko_sathi.apps.cart.utils import attach_cart_to_user


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        self._send_verification_email(self.request, user)
        messages.success(
            self.request,
            "Account created successfully. Please check your email to verify your address.",
        )
        login(self.request, user)
        attach_cart_to_user(self.request, user)
        return redirect(self.success_url)

    def _send_verification_email(self, request, user):
        uid = urlsafe_base64_encode(str(user.pk).encode())
        token = email_verification_token.make_token(user)
        verify_url = request.build_absolute_uri(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )
        subject = "Verify your Tapai Ko Sathi account"
        message = f"Namaste {user.first_name or user.email},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not create this account, please ignore this email."
        send_mail(subject, message, None, [user.email], fail_silently=True)


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


