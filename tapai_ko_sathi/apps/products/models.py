import logging
from django.db import models

logger = logging.getLogger(__name__)


class Category(models.Model):
    """
    Product category with indexing on slug for fast lookups.
    """

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    Core product model. Optimised for primary store item 'Tapai Ko Sathi'
    but flexible for future expansion.
    """

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    main_image = models.ImageField(upload_to="products/main/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional: Enter a URL to download the image from.")

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Only download if image_url is provided and main_image is empty, 
        # and we are creating or the image_url has changed.
        if self.image_url and not self.main_image:
            from django.core.files import File
            import requests
            from urllib.parse import urlparse
            import os
            from io import BytesIO
            
            try:
                response = requests.get(self.image_url, timeout=5, stream=True)
                if response.status_code == 200:
                    file_name = os.path.basename(urlparse(self.image_url).path)
                    if not file_name:
                        file_name = f"{self.slug}_image.jpg"
                    
                    # Ensure we don't block the whole save process if something goes wrong here
                    self.main_image.save(file_name, File(BytesIO(response.content)), save=False)
            except Exception as e:
                # Log error but don't crash the save process
                logger.error(f"Failed to download product image for {self.slug}: {str(e)}")
        
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    """
    Additional gallery images for a product.
    """

    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for {self.product.name}"

