from .forms import ExpenseCategoryForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm

# -------------------------
# CATEGORY LIST
# -------------------------
def expense_category_list(request):
    categories = ExpenseCategory.objects.all().order_by('-id')
    return render(request, 'expenses/category_list.html', {
        'categories': categories
    })


# -------------------------
# CATEGORY CREATE
# -------------------------
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:category_list')
    else:
        form = ExpenseCategoryForm()

    return render(request, 'expenses/category_form.html', {
        'form': form
    })




# Deleting a category
def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == "POST":
        category.delete()
        return redirect('expenses:category_list')

    return redirect('expenses:category_list')





# -------------------------
# EXPENSE LIST
# -------------------------
def expense_list(request):
    expenses = Expense.objects.select_related('category').all().order_by('-id')

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses
    })


# -------------------------
# CREATE EXPENSE
# -------------------------
def expense_create(request):

    categories = ExpenseCategory.objects.all()

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('expenses:expense_list')

    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'categories': categories
    })


# -------------------------
# DELETE EXPENSE
# -------------------------
def expense_delete(request, pk):

    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        expense.delete()

    return redirect('expenses:expense_list')