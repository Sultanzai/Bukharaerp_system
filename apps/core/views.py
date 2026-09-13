from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView
from apps.core.services.dashboard import financial_overview
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from apps.sales.models import Customer, Order
from apps.accounting.models import Transaction, PaymentRecord
from apps.purchases.models import Factory, PurchaseOrder

from django.shortcuts import render
from django.db.models import Sum, Q

from apps.investors.models import Investor, InvestorTransaction
from django.views import View



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

# ==========================================================
# Customer Statement Report - Customer List
# =========================================================
class CustomerStatementReportView(
    LoginRequiredMixin,
    ListView
):

    model = Customer

    template_name = "core/customer_statement_report.html"

    context_object_name = "customers"

    def get_queryset(self):

        customers = list(
            Customer.objects.order_by("-id")
        )

        for customer in customers:

            # ------------------------------------------
            # Customer Orders
            # ------------------------------------------

            orders = Order.objects.filter(
                customer=customer
            )

            customer.total_orders = orders.count()

            # ------------------------------------------
            # Total Order Amount
            # ------------------------------------------

            customer.total_amount = (
                orders.aggregate(
                    total=Sum("total")
                )["total"]
                or Decimal("0.00")
            )

            # ------------------------------------------
            # Customer Transactions
            # ------------------------------------------

            transactions = Transaction.objects.filter(
                party_type="customer",
                party_id=customer.id,
                reference_type="customer_order",
            )

            # ------------------------------------------
            # Total Paid
            # ------------------------------------------

            customer.total_paid = (
                PaymentRecord.objects.filter(
                    transaction__in=transactions
                ).aggregate(
                    total=Sum("paid_amount")
                )["total"]
                or Decimal("0.00")
            )

            # ------------------------------------------
            # Remaining Balance
            # ------------------------------------------

            customer.balance = (
                customer.total_amount -
                customer.total_paid
            )

        return customers




def investor_summary(request):
    investors = Investor.objects.all().order_by('name')

    investor_data = []

    for investor in investors:

        transactions = InvestorTransaction.objects.filter(
            investor=investor,
            status='completed'
        )

        total_invested = transactions.filter(
            type='investment'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_profit_distributed = transactions.filter(
            type='profit_distribution'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_withdrawn = transactions.filter(
            type='withdrawal'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        current_balance = (
            total_invested
            + total_profit_distributed
            - total_withdrawn
        )

        investor_data.append({
            'investor': investor,
            'total_invested': total_invested,
            'total_profit_distributed': total_profit_distributed,
            'total_withdrawn': total_withdrawn,
            'current_balance': current_balance,
        })

    return render(
        request,
        'core/investor_summary.html',
        {
            'investor_data': investor_data,
        }
    )




class InvestorDetailView(
    LoginRequiredMixin,
    DetailView
):
    model = Investor
    template_name = "core/investor_detail.html"
    context_object_name = "investor"

    def get_object(self):
        return get_object_or_404(
            Investor,
            id=self.kwargs["investor_id"]
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        investor = self.object

        # ------------------------------------------
        # Completed Investor Transactions
        # ------------------------------------------

        transactions = InvestorTransaction.objects.filter(
            investor=investor,
            status="completed"
        ).order_by("-created_at", "-id")


        # ------------------------------------------
        # Total Invested
        # ------------------------------------------

        total_invested = (
            transactions.filter(
                type="investment"
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )


        # ------------------------------------------
        # Total Profit Distributed
        # ------------------------------------------

        total_profit_distributed = (
            transactions.filter(
                type="profit_distribution"
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )


        # ------------------------------------------
        # Total Withdrawn
        # ------------------------------------------

        total_withdrawn = (
            transactions.filter(
                type="withdrawal"
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )


        # ------------------------------------------
        # Current Balance
        # ------------------------------------------

        current_balance = (
            total_invested
            + total_profit_distributed
            - total_withdrawn
        )


        # ------------------------------------------
        # Context
        # ------------------------------------------

        context["transactions"] = transactions

        context["total_invested"] = total_invested

        context["total_profit_distributed"] = (
            total_profit_distributed
        )

        context["total_withdrawn"] = total_withdrawn

        context["current_balance"] = current_balance

        return context



class InvestorSummaryView(LoginRequiredMixin, View):

    template_name = "core/investor_report.html"

    def get(self, request, *args, **kwargs):

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        search = request.GET.get("search", "").strip()
        date_from = request.GET.get("date_from", "").strip()
        date_to = request.GET.get("date_to", "").strip()

        # --------------------------------------------------
        # Completed Investor Transactions
        # --------------------------------------------------

        transactions = (
            InvestorTransaction.objects
            .filter(status="completed")
            .select_related(
                "investor",
                "added_by",
            )
            .order_by(
                "-transaction_date",
                "-id"
            )
        )

        # --------------------------------------------------
        # Search Investor
        # --------------------------------------------------

        if search:
            transactions = transactions.filter(
                Q(
                    investor__name__icontains=search
                )
            )

        # --------------------------------------------------
        # From Date
        # --------------------------------------------------

        if date_from:
            transactions = transactions.filter(
                transaction_date__gte=date_from
            )

        # --------------------------------------------------
        # To Date
        # --------------------------------------------------

        if date_to:
            transactions = transactions.filter(
                transaction_date__lte=date_to
            )

        # --------------------------------------------------
        # Total Invested
        # --------------------------------------------------

        total_invested = (
            transactions
            .filter(type="investment")
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # --------------------------------------------------
        # Total Profit Distributed
        # --------------------------------------------------

        total_profit_distributed = (
            transactions
            .filter(type="profit_distribution")
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # --------------------------------------------------
        # Total Withdrawn
        # --------------------------------------------------

        total_withdrawn = (
            transactions
            .filter(type="withdrawal")
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # --------------------------------------------------
        # Net Movement
        # --------------------------------------------------

        net_movement = (
            total_invested
            + total_profit_distributed
            - total_withdrawn
        )

        # --------------------------------------------------
        # Context
        # --------------------------------------------------

        context = {
            "transactions": transactions,

            "search": search,

            "date_from": date_from,

            "date_to": date_to,

            "total_invested": total_invested,

            "total_profit_distributed": (
                total_profit_distributed
            ),

            "total_withdrawn": total_withdrawn,

            "net_movement": net_movement,
        }

        return render(
            request,
            self.template_name,
            context
        )