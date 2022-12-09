import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment
from .forms import AddListingForm, CommentForm, BidForm


def index(request):
    # Query for all active listings
    active_listings = Listing.objects.filter(active=True)
    # User logged in
    if not request.user.is_anonymous:
        current_user = request.user
        # query for active listings in which current user has placed bid
        active_bidder = active_listings.filter(bid__bidder=current_user)
        context = {"active_listings": active_listings, "active_bidder": active_bidder}
    else:
        context = {"active_listings": active_listings}
    return render(request, "auctions/index.html", context)


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
            context = {"message": "Invalid username and/or password."}
            return render(request, "auctions/login.html", context)
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
            context = {"message": "Passwords must match."}
            return render(request, "auctions/register.html", context)
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            context = {"message": "Username already taken"}
            return render(request, "auctions/register.html", context)
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def search(request):
    listings = Listing.objects.filter(active=True)
    if not request.user.is_anonymous:
        listings = Listing.objects.exclude(seller_id=request.user.id).filter(active=True)
    query = request.POST.get("q")
    search_results = []
    for listing in listings:
        # Search for active listing titles matching query
        if query.lower() == listing.title.lower():
            listing_pk = listing.id
            return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))
        # Search for active listing title/s in which query is substring
        elif query.lower() in listing.title.lower():
            search_results.append(listing) 
    if len(search_results) > 0:
        context = {"message": "Did you mean?", "search_results": search_results}
    else:
        context = {"message": "No listings found."}
    return render(request, "auctions/search.html", context)


def categories(request):
    # Query for all listing categories
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "auctions/categories.html", context)


def goto_category(request, category_pk):
    # Query for active listings with specified category
    category = Category.objects.get(id=category_pk)
    listings = Listing.objects.filter(category_id=category_pk).filter(active=True)
    # Exclude current user's own listings
    if not request.user.is_anonymous:
        listings = listings.exclude(seller_id=request.user.id)
    context = {"category": category, "listings": listings}
    return render(request, "auctions/category.html", context)


@login_required(login_url="login")
def add_listing(request):
    form = AddListingForm()
    if request.method == "POST":
        # Validate form input
        form = AddListingForm(request.POST, request.FILES)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.active = True
            new_listing.current_price = new_listing.start_price
            new_listing.datetime_listed = datetime.datetime.now()
            new_listing.seller = request.user
            new_listing.highest_bidder = None
            new_listing.watching = None
            new_listing.save()
            return HttpResponseRedirect(reverse("my_listings"))
        else:
            context = {"form": form}
            return render(request, "auctions/add_listing.html", context)
    else:
        # Render form to add new listing
        context = {"form": form}
        return render(request, "auctions/add_listing.html", context)


def goto_listing(request, listing_pk):
    # Query for specified listing data
    listing = Listing.objects.get(id=listing_pk)
    listing_comments = Comment.objects.filter(listing_id=listing_pk)
    # Query total bid count
    bid_count = Bid.objects.filter(listing_id=listing_pk).count()
    # Query total watch count
    watch_count = listing.watchlist.count()
    # Query total comment count
    comment_count = listing_comments.count()
    comment_form = CommentForm()
    bid_form = BidForm()
    # User not logged in
    if request.user.is_anonymous:
        context = {
            "listing": listing,
            "listing_comments": listing_comments,
            "comment_count": comment_count,
            "bid_count": bid_count,
            "watch_count": watch_count,
        }
    # User logged in
    else:
        if request.user in listing.watchlist.all():
            user_watching = True
        else:
            user_watching = False
        context = {
            "listing": listing,
            "listing_comments": listing_comments,
            "comment_count": comment_count,
            "bid_count": bid_count,
            "watch_count": watch_count,
            "item_watched": user_watching,
            "comment_form": comment_form,
            "bid_form": bid_form,
        }
    return render(request, "auctions/listing.html", context)


@login_required(login_url="login")
def comment(request, listing_pk):
    listing = Listing.objects.get(id=listing_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        new_comment = Comment(
            message=comment_form.cleaned_data.get("message"),
            timestamp=datetime.datetime.now(),
            author_id=request.user.id,
            listing_id=listing.id,
        )
        new_comment.save()
        return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))
    else:
        return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))


@login_required(login_url="login")
def bid(request, listing_pk):
    listing = Listing.objects.get(id=listing_pk)
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        bid_price = bid_form.cleaned_data.get("bid_price")
        current_price = listing.current_price
        # Validate bit amount
        if bid_price > current_price:
            new_bid = Bid(bid_price=bid_price, bidder_id=request.user.id, listing_id=listing.id)
            # Update current listing price
            listing.current_price = bid_price
            # Update listing highest bidder
            listing.highest_bidder = request.user
            listing.save()
            new_bid.save()
            return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))
    # Invalid bid error
    messages.add_message(request, messages.ERROR, "Invalid input")
    return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))


@login_required(login_url="login")
def my_listings(request):
    # Query all listings added by current user
    user_listings = Listing.objects.filter(seller=request.user)
    context = {"user_listings": user_listings}
    return render(request, "auctions/user_listings.html", context)


@login_required(login_url="login")
def close_listing(request, listing_pk):
    listing = Listing.objects.get(id=listing_pk)
    # Confirm close listing
    if request.method == "POST":
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse("my_listings"))
    else:
        context = {"listing": listing}
        return render(request, "auctions/close_listing.html", context)


@login_required(login_url="login")
def goto_watchlist(request):
    current_user = request.user
    # Query active listings on current user's watchlist
    watched_listings = current_user.user_watching.filter(active=True)
    context = {"listings": watched_listings}
    return render(request, "auctions/user_watchlist.html", context)


@login_required(login_url="login")
def addto_watchlist(request, listing_pk):
    listing = Listing.objects.get(id=listing_pk)
    listing.watchlist.add(request.user)
    return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))


@login_required(login_url="login")
def removefrom_watchlist(request, listing_pk):
    listing = Listing.objects.get(id=listing_pk)
    listing.watchlist.remove(request.user.id)
    if "cross_button_remove_from_watchlist" in request.POST:
        return HttpResponseRedirect(reverse("goto_watchlist"))
    else:
        return HttpResponseRedirect(reverse("goto_listing", args=(listing_pk,)))


@login_required(login_url="login")
def inactive_listings(request):
    # Query for recent inactive listings
    current_user = request.user
    listings_won = Listing.objects.filter(highest_bidder=current_user).order_by("-datetime_listed").filter(active=False)
    inactive_listings = Listing.objects.filter(active=False).exclude(highest_bidder=current_user).order_by("-datetime_listed")[:20]
    print(inactive_listings)
    context = {"inactive_listings": inactive_listings, "listings_won": listings_won}
    return render(request, "auctions/inactive_listings.html", context)

@login_required(login_url="login")
def winner(request, listing_pk):
    listing_won = Listing.objects.get(id=listing_pk)
    context = {"listing_won": listing_won}
    return render(request, "auctions/winner.html", context)
