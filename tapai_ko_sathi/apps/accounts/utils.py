from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token

def send_verification_email(request, user):
    """
    Common logic to send a verification email to a user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    )
    subject = "Verify your Tapai Ko Sathi account"
    message = f"Namaste {user.first_name or user.email},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not create this account, please ignore this email."
    
    # In production, this should be an async task (e.g. Celery)
    return send_mail(subject, message, None, [user.email], fail_silently=True)
