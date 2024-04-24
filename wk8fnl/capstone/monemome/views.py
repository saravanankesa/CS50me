from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.db.models import Sum, F
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileUpdateForm, AccountForm, CategoryForm, TransactionForm
from .models import Account, Category, Transaction
from .decorators import upcoming_payments_decorator
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register(request):
        if request.method == 'POST':
            user_form = UserCreationForm(request.POST)
            account_form = AccountForm(request.POST)
            if user_form.is_valid() and account_form.is_valid():
                user = user_form.save()
                # Now create an account linked to this user
                account = account_form.save(commit=False)
                account.user = user
                account.save()
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            user_form = UserCreationForm()
            account_form = AccountForm()
        return render(request, 'monemome/register.html', {
            'user_form': user_form,
            'account_form': account_form
        })


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
@upcoming_payments_decorator
@never_cache
def index(request):
    # Log the session status
    dismissed = request.session.get('warning_dismissed', False)
    print("Warning dismissed status:", dismissed)
    # You can add context data to pass to the index template if needed.
    context = {
        'message': 'Welcome to MonE-MomE! Your personal financial tracking tool.',
    }
    return render(request, 'monemome/index.html', context)


@login_required
def profile_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    categories = Category.objects.filter(user=user)

    # Initialize forms
    profile_form = ProfileUpdateForm(instance=user)
    account_form = AccountForm()
    category_form = CategoryForm()

    if request.method == 'POST':
        if 'submit_email' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile was updated successfully.')
                return redirect('profile')  # Redirect to clear the form

        elif 'submit_account' in request.POST:
            account_form = AccountForm(request.POST)
            if account_form.is_valid():
                new_account = account_form.save(commit=False)
                new_account.user = user
                new_account.save()
                messages.success(request, 'Account added successfully.')
                return redirect('profile')  # Redirect to clear the form

        elif 'submit_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                new_category = category_form.save(commit=False)
                new_category.user = user
                new_category.save()
                messages.success(request, 'Category added successfully.')
                return redirect('profile')  # Redirect to clear the form

        else:
            profile_form = ProfileUpdateForm(instance=request.user, initial={'email': None}) 

    context = {
        'profile_form': profile_form,
        'account_form': account_form,
        'category_form': category_form,
        'accounts': accounts,
        'categories': categories
    }
    return render(request, 'monemome/profile.html', context)


@login_required
def accounts_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    # Fetching the balances along with the accounts
    accounts_with_balances = [(account, account.calculate_balance()) for account in accounts]
    # Debugging print
    for account, balance in accounts_with_balances:
        print(account.id, balance)  # This should print all account IDs and their balances
    return render(request, 'monemome/accounts.html', {'accounts_with_balances': accounts_with_balances})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, 'Account added successfully.')
            return redirect('accounts')
        else:
            logger.error("Form errors: %s", form.errors)
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'monemome/accounts.html', {'form': form})
    else:
        form = AccountForm()
        return render(request, 'monemome/accounts.html', {'form': form})


@login_required
def edit_account(request, id):
    account = get_object_or_404(Account, id=id, user=request.user)
    if request.method == 'POST':
        account.account_name = request.POST.get('name')
        account.purpose = request.POST.get('purpose')
        account.save()
        messages.success(request, 'Account updated successfully.')
        return redirect('accounts')
    else:
        # Just redirecting back for GET request or render a specific template to edit
        return render(request, 'monemome/edit_account.html', {'account': account})

@login_required
def delete_account(request, id):
    account = get_object_or_404(Account, id=id, user=request.user)  # Ensures user owns the account
    if request.method == 'POST':
        account.delete()
        messages.success(request, "Account deleted successfully.")
        return redirect('accounts')  # Redirect to accounts overview page
    else:
        # Confirm deletion
        return render(request, 'monemome/delete_account.html', {'account': account})

@login_required
def account_balances(request):
    accounts = Account.objects.filter(user=request.user)  # Fetch all accounts for the user
    balances = [(account, account.calculate_balance()) for account in accounts]  # List of tuples (account, balance)
    return render(request, 'monemome/account_balances.html', {'balances': balances})

@login_required
def categories_view(request):
    user = request.user
    sort_by = request.GET.get('sort', 'category_name')

    # Define valid sort fields to prevent errors or malicious sorting attempts
    valid_sort_fields = {'category_name', 'transaction_type', 'total_amount', 'value_score'}
    if sort_by.lstrip('-') not in valid_sort_fields:
        sort_by = 'category_name'  # Fallback to default if an invalid sort field is provided

    # Fetch categories for the logged-in user and annotate each with the sum of transaction amounts
    categories = Category.objects.filter(user=user).annotate(total_amount=Sum('transaction__amount'))
    categories = categories.order_by(sort_by)
    
    return render(request, 'monemome/categories.html', {'categories': categories})

@login_required
def categories_by_type(request, transaction_type):
    # Filter categories by the transaction type
    categories = Category.objects.filter(transaction_type=transaction_type).values('id', 'category_name')
    return JsonResponse(list(categories), safe=False)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            new_category = form.save(commit=False)  # Save the form temporarily without committing to the database
            new_category.user = request.user  # Assign the current user as the category's user
            new_category.save()  # Now save the category to the database
            messages.success(request, "Category added successfully.")
            return redirect('categories')  # Redirect to the category list page or wherever appropriate
    else:
        form = CategoryForm()
    return render(request, 'monemome/categories.html', {'form': form})

@login_required
def edit_category(request, id):
    category = get_object_or_404(Category, id=id, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('categories')  # Ensure this is the correct redirect endpoint
    else:
        form = CategoryForm(instance=category)
    return render(request, 'monemome/categories.html', {'form': form})

@login_required
def delete_category(request, id):
    category = get_object_or_404(Category, id=id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('categories')
    return render(request, 'monemome/delete_category.html', {'category': category})

@login_required
def list_transactions(request):
    logger = logging.getLogger(__name__)
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    sort_key = f"{'' if order == 'asc' else '-'}{sort}"
    logger.debug(f'Sorting by {sort} in {order} order')

    # Debugging
    print("Headers Received:", request.headers.get('X-Requested-With'))

    # Fetch the transactions according to the specified order
    transactions = Transaction.objects.filter(user=request.user).order_by(sort_key)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.debug('Handling AJAX request')
        # Render only the transaction table part for AJAX requests
        html = render_to_string('monemome/partials/transaction_table.html', {'transactions': transactions}, request=request)
        return HttpResponse(html)
    
    else:
        logger.debug('Handling full page request')
        return render(request, 'monemome/transactions.html', {'transactions': transactions})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        print(request.POST)  # Check what data is being submitted
        form = TransactionForm(request.POST, user=request.user)
        # Dynamically set the queryset for categories based on transaction type
        if 'transaction_type' in request.POST:
            transaction_type = request.POST['transaction_type']
            # Ensure it's a valid type
            if transaction_type not in [choice[0] for choice in Transaction.TRANSACTION_TYPES]:
                messages.error(request, 'Invalid transaction type selected.')
                form = TransactionForm(request.POST, user=request.user)
                return render(request, 'monemome/add_transaction.html', {'form': form})
        else:
            messages.error(request, 'Transaction type is required.')
            form = TransactionForm(request.POST, user=request.user)
            return render(request, 'monemome/add_transaction.html', {'form': form})

        form.fields['category'].queryset = Category.objects.filter(transaction_type=transaction_type)


        if form.is_valid():
            new_transaction = form.save(commit=False)
            new_transaction.user = request.user
            new_transaction.save()
            messages.success(request, 'Transaction added successfully.')
            return redirect('list_transactions')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'monemome/add_transaction.html', {'form': form})

@login_required
def edit_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            return redirect('list_transactions')
        else:
            errors = form.errors.as_text()
            messages.error(request, f"There was a problem updating the transaction: {errors}")
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    return render(request, 'monemome/edit_transaction.html', {'form': form})

@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)  # Ensure the transaction belongs to the logged-in user
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction successfully deleted.")
        return redirect('list_transactions')  # Redirect to a view where transactions are listed
    else:
        messages.error(request, "Invalid request.")
        return redirect('list_transactions')

@login_required
def pre_auth_payments(request):
    today = datetime.now().date()
    threshold_date = today + timedelta(days=5)
    transactions = Transaction.objects.filter(user=request.user, is_pre_auth=True, transaction_type='Expense')
    
    # Enhance transactions with 'due_soon' flag
    for transaction in transactions:
        transaction.due_soon = (today <= transaction.date <= threshold_date)
    
    return render(request, 'monemome/pre_auth_payments.html', {'transactions': transactions})

@login_required
def recurring_incomes(request):
    # Assuming there is a boolean field 'is_recurring' in the Transaction model that indicates recurring incomes
    recurring_transactions = Transaction.objects.filter(user=request.user, is_recurring=True, transaction_type='Income')
    return render(request, 'monemome/recurring_incomes.html', {'transactions': recurring_transactions})

@login_required
def transactions_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'monemome/transactions.html', {'transactions': transactions})

@require_POST
def dismiss_warning(request):
    request.session['warning_dismissed'] = True
    request.session.save()  # Explicitly save the session
    return HttpResponse('OK')