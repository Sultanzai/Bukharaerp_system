# apps/investors/models.py

from django.db import models


class Investor(models.Model):

    name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    email = models.EmailField(
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
        db_table = 'investors'
        ordering = ['name']

    def __str__(self):
        return self.name
    


class InvestorTransaction(models.Model):

    TYPE_CHOICES = (
        ('investment', 'Investment'),
        ('withdrawal', 'Withdrawal'),
        ('profit_distribution', 'Profit Distribution'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('hawala', 'Hawala'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    investor = models.ForeignKey(
        Investor,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    currency_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
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
        default='completed'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'investor_transactions'
        ordering = ['-transaction_date', '-id']

    def __str__(self):
        return f'{self.investor.name} - {self.get_type_display()}'
    