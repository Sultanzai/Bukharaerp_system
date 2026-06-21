from django.db import models
from apps.products.models import ProductVariant
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=255)

    phone = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(models.Model):

    ORDER_TYPES = (
        ("stock", "Stock Order"),
        ("factory", "Factory Order"),
        ("mixed", "Mixed Order"),
    )   

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    order_type = models.CharField(max_length=30, choices=ORDER_TYPES)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="draft"
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"




class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True
    )

    qty = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return str(self.product_variant)