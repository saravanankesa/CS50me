from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileUpdateForm, AccountForm, CategoryForm
from .models import Account, Category

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
@never_cache
def index(request):
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
    return render(request, 'monemome/accounts.html', {'accounts': accounts})

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