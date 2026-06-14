from django.db import models
from django.conf import settings


class Factory(models.Model):

    name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "factories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("partially_received", "Partially Received"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    )

    factory = models.ForeignKey(
        Factory,
        on_delete=models.CASCADE,
        related_name="purchase_orders"
    )

    po_number = models.CharField(
        max_length=50,
        unique=True
    )

    order_date = models.DateField()

    expected_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="draft"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    transport_tax_expenses_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "purchase_orders"
        ordering = ["-id"]

    def __str__(self):
        return self.po_number