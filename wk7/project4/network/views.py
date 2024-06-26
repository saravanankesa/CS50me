from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import NewPostForm
from .models import User, Post
import json

@login_required
def index(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            return redirect('index')
    else:
        form = NewPostForm()
    
    posts_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

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
    return HttpResponseRedirect(reverse("login"))


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

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_list = profile_user.posts.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    followers = profile_user.followers.count()
    following = profile_user.following.count()
    is_following = request.user.is_authenticated and profile_user.followers.filter(id=request.user.id).exists()

    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'followers': followers,
        'following': following,
        'is_following': is_following,
    })


@login_required
@require_POST
def follow(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)

    if request.user.username == username:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    profile_user = get_object_or_404(User, username=username)
    if profile_user.followers.filter(id=request.user.id).exists():
        profile_user.followers.remove(request.user)
    else:
        profile_user.followers.add(request.user)

    return JsonResponse({'status': 'success'})

@login_required
def following(request):
    user = request.user
    following_users = user.following.all()
    posts_list = Post.objects.filter(creator__in=following_users).order_by('-timestamp')
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'network/following.html', {'posts': posts})


@login_required
@csrf_exempt
@require_POST
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, creator=request.user)
        data = json.loads(request.body)
        post.content = data['content']
        post.save()
        return JsonResponse({'status': 'success'})
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found or not authorized to edit'}, status=404)
    

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'status': 'success', 'liked': liked, 'like_count': post.likes.count()})
