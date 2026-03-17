from rest_framework import generics, permissions
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


from tapai_ko_sathi.core.utils import api_response


class ProductListAPI(generics.ListAPIView):
    """
    Read-only API for listing active products.
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # select_related for category and prefetch images to reduce DB queries
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
        )
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(short_description__icontains=query)
                | Q(description__icontains=query)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return api_response(data=response.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)


class ProductDetailAPI(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    queryset = Product.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)


def product_list_page(request):
    from django.core.paginator import Paginator

    qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")
    category_slug = request.GET.get("category")
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    query = request.GET.get("q")
    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
        )
    paginator = Paginator(qs, 12)  # 12 items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.filter(is_active=True)
    return render(
        request,
        "products/product_list.html",
        {"products": page_obj, "categories": categories, "query": query},
    )


def product_detail_page(request, slug):
    product = get_object_or_404(Product.objects.select_related("category").prefetch_related("images"), slug=slug, is_active=True)
    return render(
        request,
        "products/product_detail.html",
        {"product": product},
    )

