from django.db import models
from django.db.models.signals import post_save, pre_delete, post_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from account.models import *
from agenda.models import *
from post.models import *
from pages.models import Pages
from images.models import Image, ImageComments


NOTIFICATION_TYPES = (
    ('FR', 'Friend Request'),
    ('FA', 'Friend Accepted'),
    ('CS', 'Comment Submitted'),
    ('CI', 'Comment Image'),
    ('PS', 'Post Shared'),
    ('PP', 'Profile Post'),
    ('FF', 'Following Acquired'),
    ('FC', 'Follow Comment'),
    ('FS', 'Follow Shared'),
    ('MC', 'Multiple Comment'),
    ('MI', 'Multiple Image Comment'),
    ('MF', 'Multiple Comment Following'),
    ('MS', 'Multiple Shared'),
    ('MD', 'Multiple Page Shared'),
    ('MM', 'Multiple Shared Following'),
    ('FM', 'Multiple Following Acquired'),
    ('MP', 'Multiple Profile Post'),
)


class Notification(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length='2', choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    #people_counter = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Friend request type
    friend_request = models.ForeignKey(FriendRequest, null=True)

    # for comments
    related_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='notification_set2')
    related_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = generic.GenericForeignKey('related_type', 'related_id')

    # General other user (used for Friend Accept, etc)
    other_user = models.ForeignKey(UserProfile, null=True, related_name='other_user')

    def people_counter(self):
        if not hasattr(self, '_people_counter'):
            setattr(self, '_people_counter', self.extra_set.filter(user_id__gt = 0).count() or 1)
        return getattr(self, '_people_counter')

    def mark_read(self):
        if not self.read:
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
        if self.type == 'MI':
            Notification.objects \
                .filter(
                    user=self.user,
                    type='CI',
                    object_id=self.content_object.id,
                    read=False
                ) \
                .update(read=True)
        if self.type == 'MF':
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='FC', \
                    object_id = self.content_object.id,
                    read = False)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type in ['MS','MD']:
            if self.type == 'MD':
                object_ids = [x.id for x in PageSharePost.objects.filter(object_id = self.content_object.id)]
            else:
                object_ids = [x.id for x in SharePost.objects.filter(object_id = self.content_object.id)]
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='PS', \
                    object_id__in = object_ids,
                    read = False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'MM':
            object_ids = [x.id for x in SharePost.objects.filter(object_id = self.content_object.id)]
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='FS', \
                    object_id__in = object_ids,
                    read = False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'FM':
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='FF', \
                    read = False)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'MP':
            original_notfs = Notification.objects.filter(user=self.user, \
                    type='PP', \
                    read = False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)


def create_friend_request_notification(sender, instance, created, **kwargs):
    #import pdb;pdb.set_trace()
    if created:
        Notification(user=instance.to_user, type='FR', friend_request=instance, content_object=instance).save()
post_save.connect(create_friend_request_notification, sender=FriendRequest)


def create_profile_post_notification(sender, instance, created, **kwargs):
    if created:
        if instance.user_to != instance.user:
            Notification(user=instance.user_to, type='PP', other_user=instance.user, content_object=instance).save()
post_save.connect(create_profile_post_notification, sender=ContentPost)


def create_share_notifiaction(sender, instance, created, **kwargs):
    if created:
        #get child post
        post = instance.get_original_post()
        if post:
            #create notification for owner
            if post.get_owner() != instance.user_to and post.get_owner() in post.following.all() \
                    and instance.user_to not in post.get_owner().get_blocked():
                Notification(user=post.get_owner(), type='PS', other_user=instance.user_to, content_object=instance).save()
            #create notifiactions for all followers of this post
            if post.following.all():
                for user in post.following.all():
                    if user != instance.user_to and user != post.get_owner() \
                            and instance.user_to not in user.get_blocked():
                        Notification(user=user, type='FS', other_user=instance.user_to, content_object=instance).save()
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('shared post was not found')
    #adding to following list
    instance.user_to.follows.add(instance)
post_save.connect(create_share_notifiaction, sender=SharePost)
post_save.connect(create_share_notifiaction, sender=PageSharePost)


def create_comment_notifiaction(sender, comment, request, **kwargs):
    news_post = comment.content_object
    if isinstance(news_post,Events):
        #notifiaction for events
        #Notification(user=comment.content_object.get_owner(), type='CS', other_user=comment.user, content_object=comment.content_object).save()
        pass
    if isinstance(news_post,NewsItem):
        news_post = news_post.get_post()
    else:
        #creating notification for owner if following
        if news_post.get_owner() != comment.user and news_post.get_owner() in news_post.get_post().following.all() \
                and comment.user not in news_post.get_owner().get_blocked():
            Notification(user=news_post.get_post().get_owner(), type='CS', other_user=comment.user, content_object=news_post).save()
        #create notifiactions for all followers of this post
        try:
            post = news_post.get_post()
            if post.following.all():
                for user in post.following.all():
                    if user != comment.user and user != post.get_owner() \
                            and comment.user not in user.get_blocked():
                        Notification(user=user, type='FC', other_user=comment.user, content_object=comment.content_object).save()
        except:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('Error in notifications')
        #adding this post to following list
        comment.user.follows.add(comment.content_object.get_post())
comment_was_posted.connect(create_comment_notifiaction)


def create_comment_image_notification(sender, instance, created, **kwargs):
    if created:
        if instance.owner != instance.image.get_owner():
            data = {
                'user': instance.image.get_owner(),
                'type': 'CI',
                'other_user': instance.owner,
                'content_object': instance.image,
                'related_object': instance,
            }
            Notification.objects.create(**data)
post_save.connect(create_comment_image_notification, sender=ImageComments)


def delete_comment_image_notification(sender, instance, **kwargs):
    if instance.owner != instance.image.owner:
        try:
            data = {
                'user': instance.image.owner,
                'type': 'CI',
                'other_user': instance.owner,
                'content_type': ContentType.objects.get_for_model(Image),
                'object_id': instance.image.id,
                'related_type': ContentType.objects.get_for_model(ImageComments),
                'related_id': instance.id,
                'read': False,
            }
            notif = Notification.objects.get(**data)
            notif.delete()
        except Notification.DoesNotExist:
            pass
post_delete.connect(delete_comment_image_notification, sender=ImageComments)


def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        if instance.from_user != instance.to_user:
            Notification(user=instance.from_user, type='FF', other_user=instance.to_user, content_object=instance).save()
post_save.connect(create_follow_notification, sender=Relationship)


def delete_dated_notifications(sender, instance, using, **kwargs):
    """Deleting for posts and comments [through newsitem object]"""
    #from celery.contrib import rdb
    #rdb.set_trace()
    if sender is Post:
        original = instance.get_inherited()
    else:
        original = instance.get_post()
    post_type = ContentType.objects.get_for_model(original)
    notf = Notification.objects.filter(content_type__pk=post_type.id, object_id=original.id)
    notf.delete()
pre_delete.connect(delete_dated_notifications, sender=Post)
pre_delete.connect(delete_dated_notifications, sender=PagePost)
pre_delete.connect(delete_dated_notifications, sender=FeedbackPost)
pre_delete.connect(delete_dated_notifications, sender=NewsItem)


def update_notification_count(sender, instance, **kwargs):
    """ merge unread notifications to one """
    if instance.type in ('CS','CI','FC','PS','FS'):
        if instance.type == 'CS': notification_type = 'MC'
        if instance.type == 'CI': notification_type = 'MI'
        if instance.type == 'FC': notification_type = 'MF'
        if instance.type == 'PS': notification_type = 'MS'
        if instance.type == 'FS': notification_type = 'MM'
        # check if notification for this object already exist
        if instance.type in ('PS','FS'):
            # get all shrepost's ids for parent (contentpost)
            if isinstance(instance.content_object, PageSharePost):
                object_ids = [x.id for x in PageSharePost.objects.filter(object_id = instance.content_object.get_original_post().id)]
                notification_type = 'MD'
            else:
                object_ids = [x.id for x in SharePost.objects.filter(object_id = instance.content_object.get_original_post().id)]
            object_id = instance.content_object.get_original_post().id
            content_object = instance.content_object.get_original_post()
        else:
            object_ids = [instance.content_object.id]
            object_id = instance.content_object.id
            content_object = instance.content_object
        data = {
            'user': instance.user,
            'type': instance.type,
            'content_type': instance.content_type,
            'object_id__in': object_ids,
            'read': False,
        }
        notfs =  Notification.objects.filter(**data)
        notfs_cnt = notfs.count()
        if notfs_cnt == 1:
            if instance.type == 'CI':
                data['type'] = notification_type
                mnotf = Notification.objects.filter(**data)
                if mnotf.count() > 0:
                    mnotf.delete()
                    notfs.filter(hidden=True).update(hidden=False)
        elif notfs_cnt > 1:
            # check if M for this comment already exist and have not yet been read
            notf = Notification.objects.filter(user=instance.user, \
                    type=notification_type, \
                    #content_type=instance.content_type, \
                    object_id = object_id,
                    read = False)
            if not notf.count():
                obj = Notification(user=instance.user, \
                        type=notification_type, \
                        #other_user=comment.user, \
                        content_object=content_object)
                # people counter
                obj.save()
                for user_notf in notfs:
                    if obj.extra_set.all():
                        if user_notf.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                            obj.extra_set.create(user_id=user_notf.other_user.id)
                    else:
                        obj.extra_set.create(user_id=user_notf.other_user.id)
            else:
                obj = notf.get()
                if obj.extra_set.all():
                    if instance.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                        obj.extra_set.create(user_id=instance.other_user.id)
            # hide all original notifications
            Notification.objects.filter(**data) \
                .filter(hidden=False) \
                .update(hidden=True)
    if instance.type in ('FF','PP'):
        if instance.type == 'FF': notification_type = 'FM'
        if instance.type == 'PP': notification_type = 'MP'
        content_object = instance.content_object
        # find all unread
        notfs =  Notification.objects.filter(user=instance.user, \
            content_type=instance.content_type, \
            type = instance.type, \
            read = False).order_by('-date')
        if notfs.count() > 1:
            # find M
            notf = Notification.objects.filter(user=instance.user, \
                    type=notification_type, \
                    read = False)
            if not notf.count():
                obj = Notification(user=instance.user, \
                        type=notification_type, \
                        content_object=content_object)
                # people counter
                obj.save()
                for user_notf in notfs:
                    if obj.extra_set.all():
                        if user_notf.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                            obj.extra_set.create(user_id=user_notf.other_user.id)
                    else:
                        obj.extra_set.create(user_id=user_notf.other_user.id)

            else:
                obj = notf.get()
                if obj.extra_set.all():
                    if instance.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                        obj.extra_set.create(user_id=instance.other_user.id)
            # hide all original notifications
            original_notfs = Notification.objects.filter(user=instance.user, \
                    type=instance.type, \
                    read = False)
            if original_notfs.count():
                original_notfs.update(hidden=True)
post_save.connect(update_notification_count, sender=Notification)
post_delete.connect(update_notification_count, sender=Notification)


class Extra(models.Model):
    notification = models.ForeignKey(Notification)
    item_id = models.IntegerField(null=True)
    user_id = models.IntegerField(default=0)

