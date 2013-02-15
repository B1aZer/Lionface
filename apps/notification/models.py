from django.db import models
from django.db.models.signals import post_save, pre_delete, post_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import comments

from django.conf import settings

from account.models import *
from agenda.models import *
from post.models import *
from pages.models import Pages
from images.models import *


NOTIFICATION_TYPES = (
    ('FR', 'Friend Request'),
    ('RR', 'Relation Request'),
    ('FA', 'Friend Accepted'),
    ('CS', 'Comment Submitted'),
    ('CI', 'Comment Image'),
    ('LI', 'Loves Image'),
    ('PS', 'Post Shared'),
    ('PP', 'Profile Post'),
    ('FF', 'Following Acquired'),
    ('FC', 'Follow Comment'),
    ('FS', 'Follow Shared'),
    ('FI', 'Follow Comment Image'),
    ('FL', 'Follow Loves Image'),
    ('LP', 'Loves Post'),
    ('DP', 'Discussion Post'),
    ('MC', 'Multiple Comment'),
    ('MI', 'Multiple Image Comment'),
    ('IM', 'Multiple Image Comment Following'),
    ('MF', 'Multiple Comment Following'),
    ('MS', 'Multiple Shared'),
    ('MD', 'Multiple Page Shared'),
    ('MM', 'Multiple Shared Following'),
    ('FM', 'Multiple Following Acquired'),
    ('MP', 'Multiple Profile Post'),
    ('ML', 'Multiple Loves Post'),
    ('II', 'Multiple Loves Image Following'),
    ('LM', 'Multiple Loves Image'),
    ('DM', 'Multiple Discussion Post'),
)


class Notification(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=2, choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    #people_counter = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
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
            setattr(self, '_people_counter', self.extra_set.filter(user_id__gt=0).count() or 1)
        return getattr(self, '_people_counter')

    def post_counter(self):
        return self.extra_set.filter(item_id__gt=0).count() or 1

    def mark_read(self):
        if not self.read:
            self.read = True
            self.save()
        # multiple
        if self.type == 'MC':
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='CS',
                                                         object_id=self.content_object.id,
                                                         read=False)
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
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='FC',
                                                         object_id=self.content_object.id,
                                                         read=False)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type in ['MS', 'MD']:
            if self.type == 'MD':
                object_ids = [x.id for x in PageSharePost.objects.filter(object_id=self.content_object.id)]
            else:
                object_ids = [x.id for x in SharePost.objects.filter(object_id=self.content_object.id)]
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='PS',
                                                         object_id__in=object_ids,
                                                         read=False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'MM':
            object_ids = [x.id for x in SharePost.objects.filter(object_id=self.content_object.id)]
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='FS',
                                                         object_id__in=object_ids,
                                                         read=False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'FM':
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='FF',
                                                         read=False)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'MP':
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='PP',
                                                         read=False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'ML':
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='LP',
                                                         read=False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.content_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)
        if self.type == 'DM':
            original_notfs = Notification.objects.filter(user=self.user,
                                                         type='DP',
                                                         read=False)
            for origianl_not in original_notfs:
                    self.extra_set.create(item_id=origianl_not.related_object.id)
            if original_notfs.count():
                original_notfs.update(read=True)

    def get_people_names(self):
        user_ids = [u.user_id for u in self.extra_set.all() if u.user_id]
        users = UserProfile.objects.filter(id__in=user_ids)
        user_names = ["<a href=\"%s\">%s</a>" % (u.get_absolute_url(), u.get_full_name()) for u in users]
        user_names = ", ".join(user_names)
        return user_names

    def get_preview(self):
        preview = ''
        if self.type in ("PP","PS","FS"):
            post = self.content_object
            try:
                if isinstance(post, SharePost):
                    post = post.content_object
                preview = post.content
            except:
                preview = ''
        if self.type in ("MP","MS","MM"):
            post_ids = [p.item_id for p in self.extra_set.all() if p.item_id]
            post = Post.objects.filter(id__in=post_ids).order_by('date')[0]
            post = post.get_inherited()
            try:
                if isinstance(post, SharePost):
                    post = post.content_object
                preview = post.content
            except:
                preview = ''
        if self.type in ('CS','FC'):
            if self.related_object:
                preview = self.related_object.comment
            else:
                # old version
                post = self.content_object
                comment = comments.get_model().objects.filter(
                            content_type=ContentType.objects.get_for_model(post),
                            object_pk=post.pk,
                            site__pk=settings.SITE_ID,
                            is_removed=False,
                            ).order_by('-submit_date')[0]
                preview = comment.comment
        if self.type in ('MC','MF'):
            comm_ids = [c.item_id for c in self.extra_set.all() if c.item_id]
            if comm_ids:
                comment = comments.get_model().objects.filter(
                            id__in=comm_ids
                            ).order_by('submit_date')[0]
            else:
                # old version
                post = self.content_object
                comment = comments.get_model().objects.filter(
                            content_type=ContentType.objects.get_for_model(post),
                            object_pk=post.pk,
                            site__pk=settings.SITE_ID,
                            is_removed=False,
                            ).order_by('submit_date')[0]
            preview = comment.comment
        return preview

    def get_events_count(self):
        count = "None"
        if self.type in ('MC','MF','MS','MM','MD','MP','ML'):
            comments = [c.item_id for c in self.extra_set.all() if c.item_id]
            count = len(comments)
        return count


def create_friend_request_notification(sender, instance, created, **kwargs):
    #import pdb;pdb.set_trace()
    if created:
        Notification(user=instance.to_user, type='FR', friend_request=instance, content_object=instance).save()
post_save.connect(create_friend_request_notification, sender=FriendRequest)


def create_discuss_post_notification(sender, instance, created, **kwargs):
    if created:
        for user in instance.topic.following.all():
            if user != instance.user:
                Notification(user=user, type='DP', other_user=instance.user, content_object=instance.topic, related_object=instance).save()
post_save.connect(create_discuss_post_notification, sender=DiscussPost)


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
    if isinstance(news_post, Events):
        #notifiaction for events
        #Notification(user=comment.content_object.get_owner(), type='CS', other_user=comment.user, content_object=comment.content_object).save()
        return
    if isinstance(news_post,NewsItem):
        news_post = news_post.get_post()
    else:
        #creating notification for owner if following
        if news_post.get_owner() != comment.user and news_post.get_owner() in news_post.get_post().following.all() \
                and comment.user not in news_post.get_owner().get_blocked():
            Notification(user=news_post.get_post().get_owner(),
                    type='CS',
                    other_user=comment.user,
                    content_object=news_post,
                    related_object = comment).save()
        #create notifiactions for all followers of this post
        try:
            post = news_post.get_post()
            if post.following.all():
                for user in post.following.all():
                    if user != comment.user and user != post.get_owner() \
                            and comment.user not in user.get_blocked():
                        Notification(user=user,
                                type='FC',
                                other_user=comment.user,
                                content_object=comment.content_object,
                                related_object = comment).save()
        except:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('Error in notifications')
        #adding this post to following list
        comment.user.follows.add(comment.content_object.get_post())
comment_was_posted.connect(create_comment_notifiaction)


def create_comment_image_notification(sender, instance, created, **kwargs):
    if created:
        if instance.owner != instance.image.get_owner() and instance.image.get_owner() in instance.image.following.all():
            data = {
                'user': instance.image.get_owner(),
                'type': 'CI',
                'other_user': instance.owner,
                'content_object': instance.image,
                'related_object': instance,
            }
            Notification.objects.create(**data)
        #create notifiactions for all followers of this post
        for user in instance.image.following.all():
            if user != instance.owner and user != instance.image.get_owner() \
                    and instance.owner not in user.get_blocked():
                data = {
                    'user': user,
                    'type': 'FI',
                    'other_user': instance.owner,
                    'content_object': instance.image,
                    'related_object': instance,
                }
                Notification.objects.create(**data)
post_save.connect(create_comment_image_notification, sender=ImageComments)


def create_love_image_notifiaction(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.post.get_owner() and instance.post.get_owner() in instance.post.following.all():
            data = {
                'user': instance.post.get_owner(),
                'type': 'LI',
                'other_user': instance.user,
                'content_object': instance.post,
                'related_object': instance,
            }
            Notification.objects.create(**data)
        #create notifiactions for all followers of this post
        for user in instance.post.following.all():
            if user != instance.user and user != instance.post.get_owner() \
                    and instance.user not in user.get_blocked():
                data = {
                    'user': user,
                    'type': 'FL',
                    'other_user': instance.user,
                    'content_object': instance.post,
                    'related_object': instance,
                }
                Notification.objects.create(**data)
post_save.connect(create_love_image_notifiaction, sender=ImageLoves)


def delete_comment_image_notification(sender, instance, **kwargs):
    if instance.owner != instance.image.owner:
        data = {
            'user': instance.image.get_owner(),
            'type': 'CI',
            'other_user': instance.owner,
            'content_type': ContentType.objects.get_for_model(Image),
            'object_id': instance.image.id,
            'related_type': ContentType.objects.get_for_model(ImageComments),
            'related_id': instance.id,
            #'read': True,
        }
        notif = Notification.objects.filter(**data)
        notif.delete()
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
    # remove image notifications
    images = Image.objects.filter(owner_type__pk=post_type.id, owner_id=original.id)
    for image in images:
        ct = ContentType.objects.get_for_model(image)
        Notification.objects.filter(content_type__pk=ct.id, object_id=image.id).delete()
pre_delete.connect(delete_dated_notifications, sender=Post)
pre_delete.connect(delete_dated_notifications, sender=PagePost)
pre_delete.connect(delete_dated_notifications, sender=FeedbackPost)
pre_delete.connect(delete_dated_notifications, sender=NewsItem)


def update_notification_count(sender, instance, **kwargs):
    """ merge unread notifications to one """
    if instance.type in ('CS', 'CI', 'LI', 'FC', 'PS', 'FS', 'FI', 'FL'):
        if instance.type == 'CS':
            notification_type = 'MC'
        if instance.type == 'CI':
            notification_type = 'MI'
        if instance.type == 'FI':
            notification_type = 'IM'
        if instance.type == 'FL':
            notification_type = 'II'
        if instance.type == 'LI':
            notification_type = 'LM'
        if instance.type == 'CI':
            notification_type = 'MI'
        if instance.type == 'FC':
            notification_type = 'MF'
        if instance.type == 'PS':
            notification_type = 'MS'
        if instance.type == 'FS':
            notification_type = 'MM'
        # check if notification for this object already exist
        if instance.type in ('PS', 'FS'):
            # get all shrepost's ids for parent (contentpost)
            if isinstance(instance.content_object, PageSharePost):
                object_ids = [x.id for x in PageSharePost.objects.filter(object_id=getattr(instance.content_object.get_original_post(), 'id', []))]
                notification_type = 'MD'
            else:
                if instance.content_object.get_original_post():
                    object_ids = [x.id for x in SharePost.objects.filter(object_id=getattr(instance.content_object.get_original_post(), 'id', []))]
                else:
                    object_ids = []
            object_id = getattr(instance.content_object.get_original_post(), 'id', None)
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
        notfs = Notification.objects.filter(**data)
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
            notf = Notification.objects.filter(user=instance.user,
                                               type=notification_type,
                                               #content_type=instance.content_type,
                                               object_id=object_id,
                                               read=False)
            # create M notifiaction
            if not notf.count():
                obj = Notification(user=instance.user,
                                   type=notification_type,
                                   #other_user=comment.user,
                                   content_object=content_object)
                # people counter
                obj.save()
                for user_notf in notfs:
                    if instance.type in ('CS','FC'):
                        obj.extra_set.create(item_id=user_notf.related_object.id)
                    if obj.extra_set.all():
                        if user_notf.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                            obj.extra_set.create(user_id=user_notf.other_user.id)
                    else:
                        obj.extra_set.create(user_id=user_notf.other_user.id)

            # update extra set
            else:
                obj = notf.get()
                if instance.type in ('CS','FC'):
                    obj.extra_set.create(item_id=instance.related_object.id)
                if obj.extra_set.all():
                    if instance.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                        obj.extra_set.create(user_id=instance.other_user.id)
            # hide all original notifications
            Notification.objects.filter(**data) \
                .filter(hidden=False) \
                .update(hidden=True)
    if instance.type in ('FF', 'PP', 'LP', 'DP'):
        if instance.type == 'FF':
            notification_type = 'FM'
        if instance.type == 'PP':
            notification_type = 'MP'
        if instance.type == 'DP':
            notification_type = 'DM'
        if instance.type == 'LP':
            notification_type = 'ML'
        content_object = instance.content_object
        # find all unread
        notfs = Notification.objects.filter(user=instance.user,
                                            content_type=instance.content_type,
                                            type=instance.type,
                                            read=False).order_by('-date')
        if notfs.count() > 1:
            # find M
            notf = Notification.objects.filter(user=instance.user,
                                               type=notification_type,
                                               read=False)
            if not notf.count():
                obj = Notification(user=instance.user,
                                   type=notification_type,
                                   content_object=content_object)
                # people counter
                obj.save()
                if not instance.type == 'DP':
                    for user_notf in notfs:
                        if obj.extra_set.all():
                            if user_notf.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                                obj.extra_set.create(user_id=user_notf.other_user.id)
                        else:
                            obj.extra_set.create(user_id=user_notf.other_user.id)

            else:
                if not instance.type == 'DP':
                    obj = notf.get()
                    if obj.extra_set.all():
                        if instance.other_user.id not in [x.user_id for x in obj.extra_set.all()]:
                            obj.extra_set.create(user_id=instance.other_user.id)
            # hide all original notifications
            original_notfs = Notification.objects.filter(user=instance.user,
                                                         type=instance.type,
                                                         read=False)
            if original_notfs.count():
                original_notfs.update(hidden=True)
post_save.connect(update_notification_count, sender=Notification)
post_delete.connect(update_notification_count, sender=Notification)


class Extra(models.Model):
    notification = models.ForeignKey(Notification)
    item_id = models.IntegerField(null=True)
    user_id = models.IntegerField(default=0)
