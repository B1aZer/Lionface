from django.db import models
from account.models import UserProfile
from pages.models import Pages

BIDS_STATUSES = (
    (0, 'Inactive'),
    (1, 'Active'),
    (2, 'Error'),
    (3, 'Winner'),
)

class Customers(models.Model):
    user = models.ForeignKey(UserProfile, related_name='customer')
    stripe_id = models.CharField(max_length=200)

class Bids(models.Model):
    user = models.ForeignKey(UserProfile, related_name='bids')
    page = models.ForeignKey(Pages, related_name='bids')
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length='1', choices=BIDS_STATUSES, default=1)
