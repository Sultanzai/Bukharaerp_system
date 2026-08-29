from decimal import Decimal
from django.db.models import IntegerField, Q, Sum
from django.db.models.functions import Coalesce

from django.db.models import Sum, Case, When, F, Value, DecimalField, ExpressionWrapper

from apps.accounting.models import Transaction
from apps.expenses.models import Expense
from apps.investors.models import Investor, InvestorTransaction
from apps.products.models import Product, ProductVariant, StockMovement
from apps.purchases.models import Factory, PurchaseOrder
from apps.sales.models import OrderItem
from apps.accounting.models import HawalaAccount, HawalaTransaction

def financial_overview():

    data = {}

    # ---------------------------------------------------
    # Investment
    # ---------------------------------------------------

    investments = (
        InvestorTransaction.objects.filter(
            type="investment",
            status="completed"
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    withdrawals = (
        InvestorTransaction.objects.filter(
            type="withdrawal",
            status="completed"
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    data["investment"] = investments - withdrawals

    # ---------------------------------------------------
    # Sales 
    # ---------------------------------------------------

    totalsales = Decimal("0.00")

    for transaction in Transaction.objects.filter(
        party_type="customer",
    ):
        totalsales += transaction.amount

    data["totalsales"] = totalsales

    # ---------------------------------------------------
    # Cash Received
    # ---------------------------------------------------

    cash = (
        Transaction.objects.filter(
            type="incoming",
            status="completed"
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    data["cash"] = cash

    data["remainingsales"] = totalsales - cash

    # ---------------------------------------------------
    # Expenses
    # ---------------------------------------------------

    expenses = (
        Expense.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    data["expenses"] = expenses



    # ---------------------------------------------------
    # Factory Payables
    # ---------------------------------------------------

    payable = Decimal("0.00")

    for transaction in Transaction.objects.filter(
        party_type="factory",
    ):
        payable += transaction.remaining_amount

    data["payables"] = payable

    # ---------------------------------------------------
    # Inventory Value
    # ---------------------------------------------------

    inventory_value = Decimal("0.00")

    for variant in ProductVariant.objects.all():
        inventory_value += Decimal(variant.stock) * variant.cost_price

    data["inventory_value"] = inventory_value


    # ---------------------------------------------------
    # Cost Of Goods
    # ---------------------------------------------------

    cost = (
        OrderItem.objects.annotate(
            item_cost=F("qty") * F("product_variant__cost_price")
        ).aggregate(
            total=Sum("item_cost")
        )["total"]
        or Decimal("0.00")
    )



    # ---------------------------------------------------
    # Hawala Balance
    # ---------------------------------------------------

    accounts = HawalaAccount.objects.all()

    total_hawala_balance = (
        HawalaTransaction.objects.filter(status="completed")
        .aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("credit") - F("debit"),
                    output_field=DecimalField()
                )
            )
        )["total"]
        or Decimal("0.00")
    )
    data["total_hawala_balance"] = total_hawala_balance


    # -----------------------------------
    # Revenue total sold amount
    # -----------------------------------
    revenue = OrderItem.objects.aggregate(
        total=Coalesce(Sum("total"), Decimal("0.00"))
    )["total"]

    # -----------------------------------
    # Cost of Goods Sold (COGS)
    # -----------------------------------
    cogs = OrderItem.objects.aggregate(
        total=Coalesce(
            Sum(
                F("qty") * F("product_variant__cost_price"),
                output_field=DecimalField()
            ),
            Decimal("0.00")
        )
    )["total"]

    data["cogs"] = cogs 

    # -----------------------------------
    # Net Profit
    # -----------------------------------
    data["profit"] = revenue - cogs + total_hawala_balance - expenses - inventory_value
    # -----------------------------------
    # Cash on Hand
    # -----------------------------------
    data["cash_on_hand"] = investments - inventory_value + total_hawala_balance - expenses - cogs 
























# ---------------------------------------------------
# Investor Report
# ---------------------------------------------------

    data["total_investors"] = Investor.objects.count()

    total_investment = (
        InvestorTransaction.objects.filter(
            type="investment",
            status="completed"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_withdrawals = (
        InvestorTransaction.objects.filter(
            type="withdrawal",
            status="completed"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_profit_shared = (
        InvestorTransaction.objects.filter(
            type="profit_distribution",
            status="completed"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    data["total_investment"] = total_investment
    data["total_profit_shared"] = total_profit_shared
    data["outstanding_amount"] = total_investment - total_withdrawals


    # ---------------------------------------------------
    # Hawala Report
    # ---------------------------------------------------

    data["total_hawala_received"] = (
        HawalaTransaction.objects.filter(
            status="completed"
        ).aggregate(
            total=Sum("credit")
        )["total"]
        or Decimal("0.00")
    )

    data["total_hawala_paid"] = (
        HawalaTransaction.objects.filter(
            status="completed"
        ).aggregate(
            total=Sum("debit")
        )["total"]
        or Decimal("0.00")
    )

    data["total_hawala_balance"] = (
        data["total_hawala_received"]
        - data["total_hawala_paid"]
    )


# ---------------------------------------------------
# Product Report
# ---------------------------------------------------

    data["total_products"] = Product.objects.count()

    data["total_variants"] = ProductVariant.objects.count()

    inventory_qty = 0
    inventory_value = Decimal("0.00")

    for variant in ProductVariant.objects.all():
        inventory_qty += variant.stock
        inventory_value += Decimal(variant.stock) * variant.cost_price

    data["inventory_qty"] = inventory_qty
    data["inventory_value"] = inventory_value


# ---------------------------------------------------
# Customer Report
# ---------------------------------------------------

    from apps.sales.models import Customer

    data["total_customers"] = Customer.objects.count()

    data["total_factories"] = Factory.objects.count()

    # Total Purchases
    data["total_purchases"] = (
        PurchaseOrder.objects.exclude(
            status="cancelled"
        ).aggregate(
            total=Sum("total")
        )["total"]
        or Decimal("0.00")
    )

    # Outstanding Factory Balance
    factory_outstanding = Decimal("0.00")

    for transaction in Transaction.objects.filter(
        party_type="factory"
    ):

        total_paid = (
            transaction.payments.aggregate(
                total=Sum("paid_amount")
            )["total"]
            or Decimal("0.00")
        )

        factory_outstanding += transaction.amount - total_paid

    data["factory_outstanding"] = factory_outstanding
    
    return data