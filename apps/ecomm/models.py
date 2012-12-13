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
    user = models.ForeignKey(UserProfile, related_name='customer', null=True, blank=True)
    page = models.ForeignKey(Pages, related_name='customer', null=True, blank=True)
    stripe_id = models.CharField(max_length=200)
    last4 = models.CharField(max_length=4, blank=True)
    type = models.CharField(max_length=200, blank=True)

    def get_last_four(self):
        if self.last4:
            return self.last4
        else:
            return '****'

    def get_type(self):
        if self.type:
            return self.type
        else:
            return 'None'


class Bids(models.Model):
    user = models.ForeignKey(UserProfile, related_name='bids')
    page = models.ForeignKey(Pages, related_name='bids')
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length='1', choices=BIDS_STATUSES, default=1)

    def get_stripe_id(self):
        return self.page.get_stripe_id_for(self.user)
