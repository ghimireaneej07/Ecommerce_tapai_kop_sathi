from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="admin_dashboard"),
    path("products/", views.product_list, name="admin_products"),
    path("products/new/", views.product_create, name="admin_product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="admin_product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="admin_product_delete"),
    path("categories/", views.category_list, name="admin_categories"),
    path("categories/new/", views.category_create, name="admin_category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.category_edit,
        name="admin_category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="admin_category_delete",
    ),
    path("orders/", views.order_list, name="admin_orders"),
    path("orders/<int:pk>/", views.order_detail, name="admin_order_detail"),
    path("users/", views.user_list, name="admin_users"),
    path("users/<int:pk>/edit/", views.user_edit, name="admin_user_edit"),
]

