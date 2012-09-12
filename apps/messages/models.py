from django.db import models
from account.models import *

# Create your models here.

class Messages(models.Model):
    user = models.ForeignKey(UserProfile)
    user_to = models.ForeignKey(UserProfile, related_name='message_to')
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    read = models.BooleanField(default=False)
