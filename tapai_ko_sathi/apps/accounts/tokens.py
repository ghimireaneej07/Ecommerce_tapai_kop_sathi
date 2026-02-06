from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Reuse Django's secure token mechanism for email verification.
    """

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_email_verified}"


email_verification_token = EmailVerificationTokenGenerator()

