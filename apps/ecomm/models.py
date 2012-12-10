from django.db import models
from account.models import UserProfile
from pages.models import Pages

class Customers(models.Model):
    user = models.ForeignKey(UserProfile, related_name='customer')
    stripe_id = models.CharField(max_length=200)

class Bids(models.Model):
    user = models.ForeignKey(UserProfile, related_name='bids')
    page = models.ForeignKey(Pages, related_name='bids')
    amount = models.IntegerField(default=0)
