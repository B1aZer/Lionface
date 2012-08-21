from django.db import models
from account.models import *
from post.models import *
from django.db.models.signals import post_save
from django.contrib.comments.signals import comment_was_posted

NOTIFICATION_TYPES = (
    ('FR', 'Friend Request'),
    ('FA', 'Friend Accepted'),
    ('CS', 'Comment Submitted'),
    ('PS', 'Post Shared'),
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

def create_comment_notifiaction(sender, comment, request, **kwargs):
    if comment.content_object.user <> comment.user:
        Notification(user=comment.content_object.user, type='CS', other_user=comment.user).save()
comment_was_posted.connect(create_comment_notifiaction)

def create_share_notifiaction(sender, instance, created, **kwargs):
    if created and instance.user <> instance.user_to:
        Notification(user=instance.user, type='PS', other_user=instance.user_to).save()
post_save.connect(create_share_notifiaction, sender=SharePost)
