from django import forms


class CheckoutForm(forms.Form):
    """
    Collects address and payment method at checkout.
    """

    full_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20)
    address_line1 = forms.CharField(max_length=255, label="Address line 1")
    address_line2 = forms.CharField(
        max_length=255, label="Address line 2", required=False
    )
    city = forms.CharField(max_length=80)
    postal_code = forms.CharField(max_length=20, required=False)

    PAYMENT_CHOICES = [
        ("esewa", "eSewa"),
        ("cod", "Cash on Delivery"),
        ("razorpay", "Razorpay (optional)"),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, widget=forms.RadioSelect
    )

