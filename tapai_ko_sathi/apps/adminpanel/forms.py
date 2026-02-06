from django import forms

from tapai_ko_sathi.apps.products.models import Category, Product
from tapai_ko_sathi.apps.orders.models import Order
from tapai_ko_sathi.apps.accounts.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "stock",
            "is_active",
            "main_image",
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "description", "is_active"]


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "is_active", "is_staff"]

