from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ListingForm
from .models import User, Listing, Bid, UserMessage
from datetime import datetime
from decimal import Decimal


@login_required
def index(request):
    current_datetime = datetime.now()
    active_listings = Listing.objects.filter(created_at__lte=current_datetime)
    unread_messages = UserMessage.objects.filter(user=request.user, read=False) if request.user.is_authenticated else None
    unread_messages.update(read=True)
    return render(request, 'auctions/index.html', {'unread_messages': unread_messages})


def logout_view(request):
    logout(request)
    return redirect('login')


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

@login_required
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

@login_required
def listing_detail(request, pk):
    listing = Listing.objects.get(pk=pk)
    return render(request, 'auctions/listing_detail.html', {'listing': listing})

@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'auctions/edit_listing.html', {'form': form, 'listing': listing})

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    listing.delete()
    return redirect('index')

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse('view_watchlist'))

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    request.user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse('listing_detail', args=(listing_id,)))

@login_required
def view_watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        bid_amount = Decimal(request.POST.get("bid_amount"))

        # Determine the required increment
        if listing.highest_bid < 99:
            increment = Decimal('5.00')
        elif 99 <= listing.highest_bid < 1000:
            increment = Decimal('10.00')
        else:
            increment = Decimal('100.00')

        # Check if the bid is in the correct increment
        if (bid_amount - listing.starting_bid) % increment == 0 and bid_amount > listing.highest_bid:
            listing.highest_bid = bid_amount
            listing.highest_bidder = request.user
            listing.save()
            bid = Bid(listing=listing, bidder=request.user, amount=bid_amount)
            bid.save()
            return redirect('listing_detail', pk=listing_id)
        else:
            error_message = f"Your bid must be in increments of ${increment} and higher than the current highest bid."
            return render(request, "auctions/listing_detail.html", {
                "listing": listing,
                "error_message": error_message
            })
    return redirect('listing_detail', pk=listing_id)


@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.user != listing.creator:
        return HttpResponseForbidden("You are not authorized to close this auction.")

    listing.active = False
    listing.winner = listing.highest_bidder
    listing.save()

    if listing.winner:
        UserMessage.objects.create(
            user=listing.winner,
            message=f'Congratulations! You won the auction for "{listing.title}".'
        )

    return redirect('listing_detail', pk=listing_id)


