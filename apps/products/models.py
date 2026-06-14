from django.db import models
from apps.purchases.models import Factory

class Category(models.Model):
    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=50
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    # factory = models.ForeignKey(
    #     Factory,
    #     on_delete=models.PROTECT,
    #     related_name="products"
    # )

    name = models.CharField(max_length=255)
    description = models.TextField( blank=True, null=True)
    BELONG_TO_CHOICES = (
    ("stock", "In Stock"),
    ("factory", "In Factory"),)
    belongto = models.CharField(
    max_length=20,
    choices=BELONG_TO_CHOICES,
    default="stock")

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["name"]

    def __str__(self):
        return self.name
    



# Product variant model 
class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    size = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    color = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    source_type = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    factory = models.ForeignKey(
        Factory,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "product_variants"

    def __str__(self):
        return self.sku
    


# Stock movement model 
class StockMovement(models.Model):

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    type = models.CharField(
        max_length=50
    )

    qty = models.IntegerField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "stock_movements"


