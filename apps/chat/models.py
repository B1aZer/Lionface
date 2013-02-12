from django.db import models
from account.models import *

# Create your models here.

class Chat(models.Model):
    user = models.ForeignKey(UserProfile)
    #tabs_to = models.TextField(blank=True)
    tabs_to = models.ManyToManyField(UserProfile, related_name='chat_tabs', symmetrical=False, through="ChatHistory")
    chat_list = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

class ChatHistory(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='chat_history')
    tab_from = models.ForeignKey(Chat, related_name='tab_from')
    date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
