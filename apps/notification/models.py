from django.db import models
from account.models import *
from post.models import *
from django.db.models.signals import post_save, pre_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


NOTIFICATION_TYPES = (
    ('FR', 'Friend Request'),
    ('FA', 'Friend Accepted'),
    ('CS', 'Comment Submitted'),
    ('PS', 'Post Shared'),
    ('PP', 'Profile Post'),
    ('FF', 'Following Acquired'),
    ('FC', 'Follow Comment'),
    ('MC', 'Multiple Comment'),
    ('MF', 'Multiple Comment Following'),
)

class Notification(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length='2', choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    people_counter = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Friend request type
    friend_request = models.ForeignKey(FriendRequest, null=True)

    # General other user (used for Friend Accept, etc)
    other_user = models.ForeignKey(UserProfile, null=True, related_name='other_user')

    def mark_read(self):
        if not self.read and self.type != 'MC':
            self.read = True
            self.save()
        # multiple
        if self.type == 'MC':
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='CS', \
                    object_id = self.content_object.id,
                    read = False)
            if original_notfs.count():
                original_notfs.update(read=True)
            self.read = True
            self.save()
        if self.type == 'MF':
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='FC', \
                    object_id = self.content_object.id,
                    read = False)
            if original_notfs.count():
                original_notfs.update(read=True)
            self.read = True
            self.save()

def create_friend_request_notification(sender, instance, created, **kwargs):
    #import pdb;pdb.set_trace()
    if created:
        Notification(user=instance.to_user, type='FR', friend_request=instance, content_object=instance).save()
post_save.connect(create_friend_request_notification, sender=FriendRequest)

def create_profile_post_notification(sender, instance, created, **kwargs):
    if created:
        if instance.user_to <> instance.user:
            Notification(user=instance.user_to, type='PP', other_user=instance.user, content_object=instance).save()
post_save.connect(create_profile_post_notification, sender=ContentPost)

def add_post_to_followings(sender, instance, created, **kwargs):
    """Follow own posts"""
    if created:
        instance.user.follows.add(instance)
post_save.connect(add_post_to_followings, sender=ContentPost)

def create_share_notifiaction(sender, instance, created, **kwargs):
    if created:
        #get child post
        post = instance.get_original_post()
        if post:
            #create notification for owner
            if post.get_owner() <> instance.user_to and post.get_owner() in post.following.all() \
                    and instance.user_to not in post.get_owner().get_blocked():
                Notification(user=post.get_owner(), type='PS', other_user=instance.user_to, content_object=instance).save()
            #create notifiactions for all followers of this post
            if post.following.all():
                for user in post.following.all():
                    if user <> instance.user_to and user <> post.get_owner() \
                            and instance.user_to not in user.get_blocked():
                        Notification(user=user, type='FS', other_user=instance.user_to, content_object=instance).save()
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('shared post was not found')
    #adding to following list
    instance.user_to.follows.add(instance)
post_save.connect(create_share_notifiaction, sender=SharePost)

def create_comment_notifiaction(sender, comment, request, **kwargs):
    news_post = comment.content_object
    #creating notification for owner if following
    if news_post.get_owner() <> comment.user and news_post.get_owner() in news_post.get_post().following.all() \
            and comment.user not in news_post.get_owner().get_blocked():
        Notification(user=comment.content_object.get_post().get_owner(), type='CS', other_user=comment.user, content_object=comment.content_object).save()
    #create notifiactions for all followers of this post
    try:
        post = news_post.get_post()
        if post.following.all():
            for user in post.following.all():
                if user <> comment.user and user <> post.get_owner() \
                        and comment.user not in user.get_blocked():
                    Notification(user=user, type='FC', other_user=comment.user, content_object=comment.content_object).save()
    except:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning('Error in notifications')
    #adding this post to following list
    comment.user.follows.add(comment.content_object.get_post())
comment_was_posted.connect(create_comment_notifiaction)

def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        if instance.from_user <> instance.to_user:
            Notification(user=instance.from_user, type='FF', other_user=instance.to_user, content_object=instance).save()
post_save.connect(create_follow_notification, sender=Relationship)

def delete_dated_notifications(sender, instance, using, **kwargs):
    """Deleting for posts and comments [through newsitem object]"""
    if sender is Post:
        original = instance.get_inherited()
    else:
        original = instance
    post_type = ContentType.objects.get_for_model(original)
    notf = Notification.objects.filter(content_type__pk=post_type.id, object_id=original.id)
    notf.delete()
pre_delete.connect(delete_dated_notifications, sender=Post)
pre_delete.connect(delete_dated_notifications, sender=NewsItem)

def update_notification_count(sender, instance, created, **kwargs):
    if instance.type in ('CS','FC'):
        if instance.type == 'CS': notification_type = 'MC'
        if instance.type == 'FC': notification_type = 'MF'
        #import pdb;pdb.set_trace()
    # check if notification for this object already exist
        notfs =  Notification.objects.filter(user=instance.user, \
                content_type=instance.content_type, \
                object_id = instance.content_object.id, \
                read = False).order_by('-date')
        if notfs.count() > 1:
            # check if MC for this comment already exist and have not yet been read
            notf = Notification.objects.filter(user=instance.user, \
                    type=notification_type, \
                    content_type=instance.content_type, \
                    object_id = instance.content_object.id,
                    read = False)
            if not notf.count():
                obj = Notification(user=instance.user, \
                        type=notification_type, \
                        #other_user=comment.user, \
                        content_object=instance.content_object)
                obj.people_counter = 2
                obj.save()
            else:
                obj = notf.get()
                obj.people_counter = obj.people_counter + 1
                obj.save()
            # hide all original notifications
            original_notfs = Notification.objects.filter(user=instance.user, \
                    type=instance.type, \
                    object_id = instance.content_object.id, \
                    read = False)
            if original_notfs.count():
                original_notfs.update(hidden=True)
post_save.connect(update_notification_count, sender=Notification)


