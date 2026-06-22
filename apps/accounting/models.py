# apps/accounting/models.py

from django.db import models


class Transaction(models.Model):

    TYPE_CHOICES = (
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    )

    PARTY_CHOICES = (
        ('customer', 'Customer'),
        ('factory', 'Factory'),
    )

    REFERENCE_CHOICES = (
        ('customer_order', 'Customer Order'),
        ('purchase_order', 'Purchase Order'),
        ('expense', 'Expense'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    party_type = models.CharField(
        max_length=20,
        choices=PARTY_CHOICES
    )

    party_id = models.BigIntegerField()

    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_CHOICES
    )

    reference_id = models.BigIntegerField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"