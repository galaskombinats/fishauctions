from pyuca import Collator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Auction, Bid, Fish, UserProfile
from .forms import AuctionForm, BidForm, UserRegistrationForm, FishForm, UserEditForm, UserProfileEditForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models


@login_required
def delete_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if not request.user.is_superuser and not request.user.userprofile.user_type == 'admin' and request.user != auction.creator:
        return redirect('auction:auction_detail', auction_id=auction.id)
    auction.delete()
    return redirect('auction:index')

@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect('homepage')
    users = User.objects.all()
    return render(request, 'registration/user_list.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('homepage')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileEditForm(request.POST, instance=user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_list')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileEditForm(instance=user.userprofile)
    return render(request, 'registration/edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('homepage')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list')

@login_required
def fish_list(request):
    if not (request.user.is_superuser or request.user.userprofile.user_type == 'admin'):
        return redirect('homepage')
    
    collator = Collator()
    fishes = sorted(Fish.objects.all(), key=lambda fish: collator.sort_key(fish.name))
    
    return render(request, 'auction/fish_list.html', {'fishes': fishes})

@login_required
def add_fish(request):
    if not (request.user.is_superuser or request.user.userprofile.user_type == 'admin'):
        return redirect('homepage')
    if request.method == 'POST':
        form = FishForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('auction:fish_list')
    else:
        form = FishForm()
    return render(request, 'auction/add_fish.html', {'form': form})

@login_required
def delete_fish(request, fish_id):
    if not (request.user.is_superuser or request.user.userprofile.user_type == 'admin'):
        return redirect('homepage')
    fish = Fish.objects.get(id=fish_id)
    fish.delete()
    return redirect('auction:fish_list')


def homepage(request):
    return render(request, 'homepage.html')

def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.userprofile.user_type == 'admin':
            auctions = Auction.objects.all().order_by('-end_time')
        else:
            auctions = Auction.objects.filter(is_ended=False).order_by('-end_time') | Auction.objects.filter(creator=request.user).order_by('-end_time')
    else:
        auctions = Auction.objects.filter(is_ended=False).order_by('-end_time')

    auctions_with_bids = []
    for auction in auctions:
        highest_bid = auction.bid_set.order_by('-amount').first()
        highest_bid_amount = highest_bid.amount if highest_bid else auction.starting_bid
        auctions_with_bids.append((auction, highest_bid_amount))
    return render(request, 'auction/index.html', {'auctions_with_bids': auctions_with_bids})


def redirect_to_homepage(request):
    return redirect('homepage')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Retrieve the user type from the form data
            user_type = form.cleaned_data.get('user_type')
            
            # Ensure the UserProfile is created without conflicts
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'user_type': user_type}
            )

            if not created:
                # If the profile already existed, update the user type
                user_profile.user_type = user_type
                user_profile.save()

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)

            if user.userprofile.user_type == 'seller':
                return redirect('auction:create_auction')
            else:
                return redirect('homepage')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('homepage')

@login_required
def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    highest_bid = auction.bid_set.order_by('-amount').first()
    winner = highest_bid.bidder if highest_bid else None
    return render(request, 'auction/auction_detail.html', {'auction': auction, 'winner': winner})

@login_required
def create_auction(request):
    try:
        user_profile = request.user.userprofile
        if user_profile.user_type not in ('seller', 'admin'):
            return redirect('homepage')
    except UserProfile.DoesNotExist:
        return redirect('homepage')

    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.creator = request.user  # Ensure the creator is set
            duration = form.cleaned_data['duration_minutes']
            auction.end_time = datetime.now() + timedelta(minutes=duration)
            auction.is_ended = False  # Ensure auction is active initially
            auction.save()
            return redirect('auction:index')
    else:
        form = AuctionForm()

    return render(request, 'auction/create_auction.html', {'form': form})

@login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    user_profile = request.user.userprofile
    if user_profile.user_type == 'seller':
        return redirect('auction:auction_detail', auction_id=auction.id)

    if auction.is_ended:
        return redirect('auction:auction_detail', auction_id=auction.id)

    if request.method == 'POST':
        form = BidForm(request.POST, auction=auction)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.auction = auction
            bid.bidder = request.user
            bid.save()
            return redirect('auction:auction_detail', auction_id=auction.id)
    else:
        form = BidForm(auction=auction)

    return render(request, 'auction/place_bid.html', {'form': form, 'auction': auction})

@login_required
def end_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if request.user != auction.creator:
        return redirect('auction:auction_detail', auction_id=auction.id)
    auction.end_time = datetime.now()
    auction.is_ended = True
    auction.save()
    return redirect('auction:auction_detail', auction_id=auction.id)

@login_required
def delete_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if not request.user.is_superuser and request.user.userprofile.user_type != 'admin' and request.user != auction.creator:
        return redirect('auction:auction_detail', auction_id=auction.id)
    auction.delete()
    return redirect('auction:index')


@login_required
def user_profile(request):
    user = request.user
    acquired_auctions = Bid.objects.filter(bidder=user, auction__is_ended=True).order_by('-amount').values('auction').distinct()
    acquired_auctions = Auction.objects.filter(id__in=[bid['auction'] for bid in acquired_auctions])

    if user.is_superuser:
        created_listings = list(Auction.objects.filter(creator=user, is_ended=False))
        participated_listings = list(Auction.objects.filter(bid__bidder=user, is_ended=False).distinct())
        active_listings = list({auction.id: auction for auction in created_listings + participated_listings}.values())
    elif user.userprofile.user_type == 'seller':
        active_listings = Auction.objects.filter(creator=user, is_ended=False)
    else:  # user is a buyer
        active_listings = Auction.objects.filter(bid__bidder=user, is_ended=False).distinct()
    
    listings_with_bids = []
    for auction in active_listings:
        highest_bid = auction.bid_set.order_by('-amount').first()
        listings_with_bids.append((auction, highest_bid))
    
    return render(request, 'registration/profile.html', {'acquired_auctions': acquired_auctions, 'listings_with_bids': listings_with_bids})
