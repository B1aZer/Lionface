from django.db import models
from account.models import *

# Create your models here.

class Chat(models.Model):
    user = models.ForeignKey(UserProfile)
    tabs_to = models.TextField(blank=True)
    date = models.DateTimeField(auto_now=True)
