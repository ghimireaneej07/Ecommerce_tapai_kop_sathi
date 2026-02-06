from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404, render

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductListAPI(generics.ListAPIView):
    """
    Read-only API for listing active products.
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class ProductDetailAPI(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    queryset = Product.objects.filter(is_active=True)


def product_list_page(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    return render(
        request,
        "products/product_list.html",
        {"products": products, "categories": categories},
    )


def product_detail_page(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(
        request,
        "products/product_detail.html",
        {"product": product},
    )

