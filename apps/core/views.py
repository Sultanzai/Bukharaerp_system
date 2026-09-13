from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.core.services.dashboard import financial_overview
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.sales.models import Customer, Order
from apps.accounting.models import Transaction, PaymentRecord

from decimal import Decimal


from apps.purchases.models import Factory, PurchaseOrder


class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["financial"] = financial_overview()

        return context
    
class ReportView(LoginRequiredMixin, TemplateView):
    template_name = "core/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(financial_overview())
        return context






class CustomerStatementView(LoginRequiredMixin, TemplateView):
    template_name = "core/customer_statement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer_id = self.kwargs["customer_id"]

        customer = get_object_or_404(
            Customer,
            pk=customer_id
        )

        # ---------------------------------------------------------
        # CUSTOMER ORDERS
        # ---------------------------------------------------------

        orders = (
            Order.objects
            .filter(customer=customer)
            .order_by("created_at", "id")
        )

        # ---------------------------------------------------------
        # CUSTOMER ORDER TRANSACTIONS
        # ---------------------------------------------------------

        transactions = (
            Transaction.objects
            .filter(
                party_type="customer",
                party_id=customer.id,
                reference_type="customer_order",
            )
            .prefetch_related("payments")
            .order_by("created_at", "id")
        )

        # ---------------------------------------------------------
        # BUILD STATEMENT
        # ---------------------------------------------------------

        statement_rows = []

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        # ---------------------------------------------------------
        # ORDERS = DEBIT
        # ---------------------------------------------------------

        for order in orders:

            amount = order.total or Decimal("0.00")

            # Order.created_at is datetime.
            # Convert it to date so it can be compared with
            # PaymentRecord.payment_date.
            order_date = order.created_at.date()

            transaction = next(
                (
                    transaction
                    for transaction in transactions
                    if transaction.reference_id == order.id
                ),
                None
            )

            statement_rows.append({
                "date": order_date,
                "sort_datetime": order.created_at,
                "reference": f"ORD-{order.id}",
                "description": "Customer Order",
                "type": "debit",
                "debit": amount,
                "credit": Decimal("0.00"),
                "order": order,
                "transaction": transaction,
                "payment": None,
            })

            total_debit += amount

        # ---------------------------------------------------------
        # PAYMENTS = CREDIT
        # ---------------------------------------------------------

        for transaction in transactions:

            for payment in transaction.payments.all():

                amount = payment.paid_amount or Decimal("0.00")

                # payment_date is already a date.
                payment_date = payment.payment_date

                statement_rows.append({
                    "date": payment_date,
                    "sort_datetime": payment_date,
                    "reference": f"PAY-{payment.id}",
                    "description": (
                        f"Payment - "
                        f"{payment.get_payment_method_display()}"
                    ),
                    "type": "credit",
                    "debit": Decimal("0.00"),
                    "credit": amount,
                    "order": None,
                    "transaction": transaction,
                    "payment": payment,
                })

                total_credit += amount

        # ---------------------------------------------------------
        # SORT STATEMENT
        # ---------------------------------------------------------
        #
        # Both rows now use compatible values for sorting.
        #
        # For same-day transactions:
        # debit/order rows are placed before payments.
        # ---------------------------------------------------------

        statement_rows.sort(
            key=lambda row: (
                row["date"],
                0 if row["type"] == "debit" else 1,
                row["reference"],
            )
        )

        # ---------------------------------------------------------
        # RUNNING BALANCE
        # ---------------------------------------------------------

        running_balance = Decimal("0.00")

        for row in statement_rows:

            running_balance += row["debit"]
            running_balance -= row["credit"]

            row["balance"] = running_balance

        # ---------------------------------------------------------
        # FINAL BALANCE
        # ---------------------------------------------------------

        balance_due = total_debit - total_credit

        # ---------------------------------------------------------
        # STATEMENT DATE
        # ---------------------------------------------------------

        from datetime import date

        statement_date = date.today()

        # ---------------------------------------------------------
        # CONTEXT
        # ---------------------------------------------------------

        context.update({
            "customer": customer,

            "statement_rows": statement_rows,

            "total_debit": total_debit,
            "total_credit": total_credit,

            "balance_due": balance_due,
            "running_balance": running_balance,

            "statement_date": statement_date,
        })

        return context



# ==========================================================
# Factory / Supplier Statement
# ==========================================================

class FactoryStatementView(LoginRequiredMixin, TemplateView):

    template_name = "core/factory_statement.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        factory_id = self.kwargs["factory_id"]

        factory = get_object_or_404(
            Factory,
            pk=factory_id
        )

        # --------------------------------------------------
        # Purchase Orders
        # --------------------------------------------------

        purchase_orders = (
            PurchaseOrder.objects
            .filter(factory=factory)
            .order_by("order_date", "id")
        )

        # --------------------------------------------------
        # Factory Transactions
        # --------------------------------------------------

        transactions = (
            Transaction.objects
            .filter(
                party_type="factory",
                party_id=factory.id,
                reference_type="purchase_order",
            )
            .prefetch_related("payments")
            .order_by("created_at", "id")
        )

        # --------------------------------------------------
        # Statement Rows
        # --------------------------------------------------

        statement_rows = []

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        # --------------------------------------------------
        # Purchase Orders = DEBIT
        # --------------------------------------------------

        for purchase_order in purchase_orders:

            amount = (
                purchase_order.total
                or Decimal("0.00")
            )

            transaction = next(
                (
                    transaction
                    for transaction in transactions
                    if transaction.reference_id == purchase_order.id
                ),
                None
            )

            statement_rows.append({
                "date": purchase_order.order_date,

                "sort_datetime": purchase_order.order_date,

                "reference": purchase_order.po_number,

                "description": "Purchase Order",

                "type": "debit",

                "debit": amount,

                "credit": Decimal("0.00"),

                "purchase_order": purchase_order,

                "transaction": transaction,

                "payment": None,
            })

            total_debit += amount

        # --------------------------------------------------
        # Payments = CREDIT
        # --------------------------------------------------

        for transaction in transactions:

            for payment in transaction.payments.all():

                amount = (
                    payment.paid_amount
                    or Decimal("0.00")
                )

                payment_date = payment.payment_date

                statement_rows.append({
                    "date": payment_date,

                    "sort_datetime": payment_date,

                    "reference": f"PAY-{payment.id}",

                    "description": (
                        f"Payment - "
                        f"{payment.get_payment_method_display()}"
                    ),

                    "type": "credit",

                    "debit": Decimal("0.00"),

                    "credit": amount,

                    "purchase_order": None,

                    "transaction": transaction,

                    "payment": payment,
                })

                total_credit += amount

        # --------------------------------------------------
        # Sort Statement
        # --------------------------------------------------

        statement_rows.sort(
            key=lambda row: (
                row["date"],
                0 if row["type"] == "debit" else 1,
                row["reference"],
            )
        )

        # --------------------------------------------------
        # Running Balance
        # --------------------------------------------------

        running_balance = Decimal("0.00")

        for row in statement_rows:

            running_balance += row["debit"]

            running_balance -= row["credit"]

            row["balance"] = running_balance

        # --------------------------------------------------
        # Balance Due
        # --------------------------------------------------

        balance_due = (
            total_debit -
            total_credit
        )

        # --------------------------------------------------
        # Statement Date
        # --------------------------------------------------

        from datetime import date

        statement_date = date.today()

        # --------------------------------------------------
        # Context
        # --------------------------------------------------

        context.update({

            "factory": factory,

            "statement_rows": statement_rows,

            "total_debit": total_debit,

            "total_credit": total_credit,

            "balance_due": balance_due,

            "running_balance": running_balance,

            "statement_date": statement_date,

        })

        return context