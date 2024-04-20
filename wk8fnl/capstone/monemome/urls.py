from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='monemome/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='monemome/password_change_done.html'), name='password_change_done'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('accounts/edit/<int:id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:id>/', views.delete_account, name='delete_account'),
    path('categories/', views.categories_view, name='categories'),
    path('categories/edit/<int:id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('transactions/list/', views.list_transactions, name='list_transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:id>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/pre-auth/', views.pre_auth_payments, name='pre_auth_payments'),
    path('transactions/recurring/', views.recurring_incomes, name='recurring_incomes'),
    path('api/categories/<str:transaction_type>/', views.categories_by_type, name='categories_by_type'),
    path('accounts/list', views.accounts_view, name='list_accounts'), 
    path('accounts/balances/', views.account_balances, name='account_balances'),
    path('dismiss-warning/', views.dismiss_warning, name='dismiss_warning'),
]
