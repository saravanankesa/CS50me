from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ListingForm

from .models import User, Listing


def index(request):
    # Retrieve latest listings
    latest_listings = Listing.objects.all().order_by('-created_at')[:5]  # Get the latest 5 listings
    return render(request, 'auctions/index.html', {'latest_listings': latest_listings})

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            # Save the form data to create a new listing
            listing = form.save(commit=False)
            listing.creator_id = request.user.id
            listing.save()
            return redirect('listing_detail', pk=listing.pk)  # Redirect to the listing after creating the listing
    else:
        form = ListingForm()

    return render(request, 'auctions/create_listing.html', {'form': form})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'auctions/listing_detail.html', {'listing': listing})
