from django.db import models
from account.models import *
from django.db.models.signals import post_save

NOTIFICATION_TYPES = (
    ('FR', 'Friend Request'),
    ('FA', 'Friend Accepted'),
)

class Notification(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length='2', choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    
    # Friend request type
    friend_request = models.ForeignKey(FriendRequest, null=True)
    
    # General other user (used for Friend Accept, etc)
    other_user = models.ForeignKey(UserProfile, null=True, related_name='other_user')
    
    def mark_read(self):
        if not self.read:
            self.read = True
            self.save()
    
def create_friend_request_notification(sender, instance, created, **kwargs):
    if created:
        Notification(user=instance.to_user, type='FR', friend_request=instance).save()
post_save.connect(create_friend_request_notification, sender=FriendRequest)