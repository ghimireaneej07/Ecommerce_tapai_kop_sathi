from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from tapai_ko_sathi.apps.accounts.models import User
from tapai_ko_sathi.apps.adminpanel.forms import (
    CategoryForm,
    OrderStatusForm,
    ProductForm,
    UserForm,
)
from tapai_ko_sathi.apps.orders.models import Order
from tapai_ko_sathi.apps.products.models import Category, Product


def staff_required(view_func):
    """
    Decorator: allow only logged-in staff members into custom admin panel.
    """

    decorated = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated


@staff_required
def dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = (
        Order.objects.filter(status__in=["paid", "completed"]).aggregate(
            s=Sum("total_amount")
        )["s"]
        or 0
    )
    pending_orders = Order.objects.filter(status="pending").count()
    recent_orders = Order.objects.order_by("-created_at")[:5]

    last_7_days = timezone.now() - timedelta(days=7)
    orders_per_day = (
        Order.objects.filter(created_at__gte=last_7_days)
        .extra(select={"day": "DATE(created_at)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "recent_orders": recent_orders,
        "orders_per_day": orders_per_day,
    }
    return render(request, "adminpanel/dashboard.html", context)


@staff_required
def product_list(request):
    products = Product.objects.all().select_related("category")
    return render(request, "adminpanel/product_list.html", {"products": products})


@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect("admin_products")
    else:
        form = ProductForm()
    return render(request, "adminpanel/product_form.html", {"form": form})


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("admin_products")
    else:
        form = ProductForm(instance=product)
    return render(
        request,
        "adminpanel/product_form.html",
        {"form": form, "product": product},
    )


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("admin_products")
    return render(
        request, "adminpanel/confirm_delete.html", {"object": product, "type": "product"}
    )


@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "adminpanel/category_list.html", {"categories": categories})


@staff_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("admin_categories")
    else:
        form = CategoryForm()
    return render(request, "adminpanel/category_form.html", {"form": form})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("admin_categories")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "adminpanel/category_form.html",
        {"form": form, "category": category},
    )


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("admin_categories")
    return render(
        request, "adminpanel/confirm_delete.html", {"object": category, "type": "category"}
    )


@staff_required
def order_list(request):
    orders = Order.objects.all().select_related("user")
    return render(request, "adminpanel/order_list.html", {"orders": orders})


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated.")
            return redirect("admin_order_detail", pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
    return render(
        request,
        "adminpanel/order_detail.html",
        {"order": order, "form": form},
    )


@staff_required
def user_list(request):
    users = User.objects.all()
    return render(request, "adminpanel/user_list.html", {"users": users})


@staff_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("admin_users")
    else:
        form = UserForm(instance=user)
    return render(
        request,
        "adminpanel/user_form.html",
        {"form": form, "user_obj": user},
    )

