# apps/accounting/models.py

from django.db import models
from decimal import Decimal
from django.db.models import Sum

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
        max_length=100,
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
    



    @property
    def paid_amount(self):

        return (
            self.payments.aggregate(
                total=Sum("paid_amount")
            )["total"]
            or Decimal("0.00")
        )


    @property
    def remaining_amount(self):

        return self.amount - self.paid_amount
    


class PaymentRecord(models.Model):

    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('Hawala', 'Hawala'),
        ('bank', 'Bank'),
        ('cheque', 'Cheque'),
    )

    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHODS
    )

    code_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_date = models.DateField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "payment_records"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.id}"