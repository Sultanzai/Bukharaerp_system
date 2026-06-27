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
    



# Hawala Model 

class HawalaAccount(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
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

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "hawala_accounts"
        ordering = ["name"]

    def __str__(self):
        return self.name


class HawalaTransaction(models.Model):

    TRANSACTION_TYPES = (

        ("deposit", "Deposit"),

        ("supplier_payment", "Supplier Payment"),

        ("customer_receipt", "Customer Receipt"),

        ("withdrawal", "Withdrawal"),

        ("adjustment", "Adjustment"),

    )

    STATUS_CHOICES = (

        ("pending", "Pending"),

        ("completed", "Completed"),

        ("cancelled", "Cancelled"),

    )

    PAYMENT_METHODS = (

        ("cash", "Cash"),

        ("bank", "Bank"),

        ("other", "Other"),

    )

    hawala_account = models.ForeignKey(
        HawalaAccount,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPES
    )

    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    currency_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="cash"
    )

    reference_type = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    reference_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    transaction_date = models.DateField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "hawala_transactions"
        ordering = [
            "-transaction_date",
            "-id"
        ]

    def __str__(self):
        return (
            f"{self.hawala_account.name} - "
            f"{self.get_transaction_type_display()}"
        )