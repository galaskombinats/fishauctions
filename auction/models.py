# auction/models.py
from django.db import models
from django.contrib.auth.models import User

class Fish(models.Model):
    name = models.CharField(max_length=100)
    # other fields...

    def __str__(self):
        return self.name

class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()
    end_time = models.DateTimeField(editable=False)
    image = models.ImageField(upload_to='fish_images/', null=True, blank=True)
    size_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_auctions')  # Make nullable
    is_ended = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('seller', 'Seller'),
        ('bidder', 'Bidder'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username

class TaskExecution(models.Model):
    task_name = models.CharField(max_length=255)
    execution_time = models.DateTimeField(auto_now_add=True)
    auction_id = models.IntegerField()

    def __str__(self):
        return f"{self.task_name} executed at {self.execution_time} for auction_id {self.auction_id}"