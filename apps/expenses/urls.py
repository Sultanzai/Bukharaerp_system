from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path('categories/', views.expense_category_list, name='category_list'),
    path('categories/create/', views.expense_category_create, name='category_create'),
    # DELETE
    path('categories/delete/<int:pk>/', views.expense_category_delete, name='category_delete'),
    
    # expenses
    path('', views.expense_list, name='expense_list'),
    path('create/', views.expense_create, name='expense_create'),
    path('delete/<int:pk>/', views.expense_delete, name='expense_delete'),
]