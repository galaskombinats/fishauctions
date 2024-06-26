from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Fish(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    # other fields...

    def __str__(self):
        return self.name

class Auction(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE, verbose_name=_("Fish"))
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Starting Bid"))
    duration_minutes = models.IntegerField(verbose_name=_("Duration (minutes)"))
    end_time = models.DateTimeField(editable=False, verbose_name=_("End Time"))
    image = models.ImageField(upload_to='fish_images/', null=True, blank=True, verbose_name=_("Image"))
    size_cm = models.FloatField(null=True, blank=True, verbose_name=_("Size (cm)"))
    weight_kg = models.FloatField(null=True, blank=True, verbose_name=_("Weight (kg)"))
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_auctions', verbose_name=_("Creator"))  # Make nullable
    is_ended = models.BooleanField(default=False, verbose_name=_("Is Ended"))

    def __str__(self):
        return self.title

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, verbose_name=_("Auction"))
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', verbose_name=_("Bidder"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    bid_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Bid Time"))

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('seller', _('Seller')),
        ('bidder', _('Bidder')),
        ('admin', _('Admin')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name=_("User Type"))

    def __str__(self):
        return self.user.username

class TaskExecution(models.Model):
    task_name = models.CharField(max_length=255, verbose_name=_("Task Name"))
    execution_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Execution Time"))
    auction_id = models.IntegerField(verbose_name=_("Auction ID"))

    def __str__(self):
        return f"{self.task_name} executed at {self.execution_time} for auction_id {self.auction_id}"
