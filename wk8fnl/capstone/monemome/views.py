from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import ProfileUpdateForm, TransactionForm
from .models import Transaction, Category, Account
import logging

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']  # Get the email from the form
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        # Create a new user with the provided email
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        return redirect('index')
    return render(request, 'monemome/register.html')

@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('index'))  # Redirect to the index page after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'monemome/login.html')  # Render the login template

@login_required
@never_cache
def index(request):
    # You can add context data to pass to the index template if needed.
    context = {
        'message': 'Welcome to MonE-MomE! Your personal financial tracking tool.',
    }
    return render(request, 'monemome/index.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'monemome/profile.html', {'form': form})

@login_required
@never_cache
def transactions(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            # Handle new account creation
            account_name = form.cleaned_data.get('account_name')
            if account_name and not Account.objects.filter(user=request.user, name=account_name).exists():
                Account.objects.create(user=request.user, name=account_name)
            
            # Handle new category creation
            category_name = form.cleaned_data.get('category')
            if category_name and not Category.objects.filter(user=request.user, name=category_name).exists():
                Category.objects.create(user=request.user, name=category_name, transaction_type=transaction.transaction_type)
            
            transaction.save()
            messages.success(request, "Transaction added successfully!")
            return redirect('transactions')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TransactionForm(user=request.user)

    user_transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    unique_account_names = Account.objects.filter(user=request.user).values_list('name', flat=True).distinct()
    
    context = {
        'form': form,
        'transactions': user_transactions,
        'unique_account_names': unique_account_names
    }
    return render(request, 'monemome/transactions.html', context=context)

def get_categories(request):
    transaction_type = request.GET.get('transaction_type')
    categories = list(Category.objects.filter(transaction_type=transaction_type)
                                      .values_list('name', flat=True))
    return JsonResponse({'categories': categories})

@login_required
@never_cache
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'transactions/list.html', {'transactions': transactions})