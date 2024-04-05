from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect

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
def index(request):
    # You can add context data to pass to the index template if needed.
    context = {
        'message': 'Welcome to MonE-MomE! Your personal financial tracking tool.',
    }
    return render(request, 'monemome/index.html', context)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'transactions/list.html', {'transactions': transactions})