from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import NewPostForm
from .models import User, Post

@login_required
def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            return redirect('index')
    else:
        form = NewPostForm()
    return render(request, "network/index.html", {'form': form, 'posts': posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login_view"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def new_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            return redirect('index')
    else:
        form = NewPostForm()
    return render(request, 'network/new_post.html', {'form': form})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().order_by('-timestamp')
    followers = user.followers.count()
    following = user.following.count()
    return render(request, 'network/profile.html', {
        'user': user,
        'posts': posts,
        'followers': followers,
        'following': following
    })

def follow(request, username):
    if request.method == "POST":
        user_to_follow = get_object_or_404(User, username=username)
        if request.user in user_to_follow.followers.all():
            user_to_follow.followers.remove(request.user)
        else:
            user_to_follow.followers.add(request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def following(request):
    user = request.user
    following_users = user.following.all()
    posts = Post.objects.filter(creator__in=following_users).order_by('-timestamp')
    return render(request, 'network/following.html', {'posts': posts})
