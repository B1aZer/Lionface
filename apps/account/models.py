import os
from itertools import chain

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.query import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError

from django.utils import simplejson as json

from .fields import ImageWithThumbField, CoordsField
from .storage import ImageStorage


FILTER_TYPE = (
    ('F', 'Friend Feed'),
    ('W', 'Following Feed'),
    ('T', 'Tag Feed'),
    ('P', 'Pages Feed'),
    ('A', 'Public Feed'),
)

RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 0
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
)


class FriendRequest(models.Model):
    from_user = models.ForeignKey('UserProfile', related_name='from_user')
    to_user = models.ForeignKey('UserProfile', related_name='to_user')
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    # Accept the friend request
    def accept(self):
        from notification.models import Notification
        from post.models import FriendPost
        self.from_user.friends.add(self.to_user)
        self.from_user.save()
        # following removes current's followers
        #import pdb;pdb.set_trace()
        if self.to_user in self.from_user.get_following_active():
            #self.from_user.remove_following(self.to_user)
            self.from_user.block_following(self.to_user)
        # for followers
        if self.to_user in self.from_user.get_followers_active():
            self.from_user.block_follower(self.to_user)
        Notification(user=self.from_user, type='FA', other_user=self.to_user, content_object = self).save()
        FriendPost(user=self.from_user, friend=self.to_user, user_to=self.to_user).save()
        #AddFriendToFeed.delay(self.from_user, self.to_user)
        #AddFriendToFeed.delay(self.to_user, self.from_user)
        self.delete()

    # Decline the friend request
    def decline(self):
        self.delete()

    def save(self, *args, **kwargs):
        send = False
        if self.to_user.check_visiblity('add_friend', self.from_user):
            send = True
        if send:
            super(FriendRequest, self).save(*args, **kwargs)
        return send


class UserProfile(User):
    # Logic is if a friend is in the 'friends' collection then they are verified.
    # If there is an active FriendRequest then it's still pending.
    friends = models.ManyToManyField('self', related_name='friends')
    hidden = models.ManyToManyField('self', symmetrical=False, related_name='hidden_from')
    blocked = models.ManyToManyField('self', symmetrical=False, related_name='blocked_from')
    photo = ImageWithThumbField(upload_to="uploads/images", verbose_name="Please Upload a Photo Image", default='uploads/images/noProfilePhoto.png')
    filters = models.CharField(max_length='10', choices=FILTER_TYPE, default="F")
    followers = models.ManyToManyField('self', related_name='following', symmetrical=False, through="Relationship")
    optional_name = models.CharField(max_length='200', default="")

    def has_friend(self, user):
        return self.friends.filter(id=user.id).count() > 0

    def has_friends_friend(self, user):
        for friend in self.friends.all():
            if self.friends.filter(id=friend.id).count() > 0 or friend == user:
                return True
        return False

    def get_mutual_friends(self, user):
        if not user:
            return

        mutual_friends = 0
        my_freinds = self.friends.all()
        his_friends = user.friends.all()

        for friend in my_freinds:
            if friend in his_friends:
                mutual_friends += 1

        return mutual_friends

    def list_mutual_friends(self, user):
        if not user:
            return

        mutual_friends = []
        my_freinds = self.friends.all()
        his_friends = user.friends.all()

        for friend in my_freinds:
            if friend in his_friends:
                mutual_friends.append(friend)

        return mutual_friends

    def get_degree_for(self, user):
        from degrees.models import Degree
        deg = None
        deg = Degree.objects.filter(from_user=self, to_user=user)
        if deg.count() > 0:
            deg = deg[0].distance
        """
        for friend in self.friends.all():
            if friend.id == user.id:
                return "%s|%s" % (0,deg)

        for friend in self.friends.all():
            for ffriend in friend.friends.all():
                if ffriend.id == user.id:
                    return "%s|%s" % (1,deg)

        for friend in self.friends.all():
            for ffriend in friend.friends.all():
                for fffriend in ffriend.friends.all():
                    if fffriend.id == user.id:
                        return "%s|%s" % (2,deg)
                    """
        return deg
        """
        dos = Degree.objects.filter(from_user=self, to_user=user)
        if dos.count() > 0:
            return dos[0].distance
        else:
            return 'none'
        """

    def get_friends(self):
        blocked_ids = [x.id for x in self.get_blocked_self()]
        return self.friends.exclude(id__in=blocked_ids)

    def get_friends_count(self, user=None):
        blocked_id = [x.id for x in self.get_blocked()]
        friends = self.friends.exclude(id__in=blocked_id)
        if user:
            friends = friends.exclude(id=user.id)
        friends_count = friends.count()
        return friends_count

    def has_friend_request(self, user):
        return FriendRequest.objects.filter(Q(from_user=self, to_user=user) | Q(to_user=self, from_user=user)).count() > 0

    def in_hidden(self, user):
        return self.hidden.filter(id=user.id).count() > 0

    def get_blocked(self):
        blocked = [x for x in self.blocked.all()]
        blocked_from = [x for x in self.blocked_from.all()]
        blocked_all = list(set(list(chain(blocked,blocked_from))))
        return blocked_all

    def get_blocked_ids(self):
        blocked = [x.id for x in self.blocked.all()]
        blocked_from = [x.id for x in self.blocked_from.all()]
        blocked_all = list(set(list(chain(blocked,blocked_from))))
        return blocked_all

    def get_blocked_self(self):
        return self.blocked.all()

    def get_blocked_from(self):
        return self.blocked_from.all()

    # Returns a queryset for all news items this user can see in date order.
    def get_news(self):
        from post.models import NewsItem
        #return NewsItem.objects.filter(user=self, hidden=False).order_by('date').reverse()
        #User can see all public messages,
        #not only his
        return NewsItem.objects.filter(hidden=False).order_by('date').reverse()

    # Return feed dpending on selected filters
    def get_messages(self):
        from post.models import NewsItem
        filters = self.filters.split(',')
        # Friends
        if 'F' in filters:
            hidden_list = [x.id for x in self.hidden.all()]
            user_list = self.friends.all().exclude(id__in=hidden_list)
        else:
            user_list = []
        # Following
        if 'W' in filters:
            following = self.get_following_active()
            following = [x for x in following if x.check_visiblity('follow',self)]
        else:
            following = []
        # Blocked
        if self.get_blocked():
            blocked = [x for x in self.get_blocked()]
        else:
            blocked = []
        user_list = list(set(list(chain(user_list,following))))
        return NewsItem.objects.filter(user__in=user_list).exclude(user__in=blocked).exclude(post__user=self).order_by('date').reverse()

    def get_filters(self):
        filters = self.filters.split(',')
        if self.filters:
            return filters
        else:
            return []

    def get_active_tags(self):
        tags = self.user_tag_set.all()
        tags = [x for x in tags if x.active]
        if tags:
            return tags
        else:
            return []

    def get_options(self):
        options = {}
        for option in self.useroptions_set.all():
            options[option.name] = option.value
        return options

    def get_albums(self):
        return self.albums_set.all().order_by('position')

    def get_album_count(self):
        return self.albums_set.count()

    def check_option(self,name,value=None):
        name = "option_%s" % name
        try:
            option = self.useroptions_set.get(name=name)
            if value:
                if option.value == value:
                    return True
                else:
                    return False
            else:
                return option.value
        except ObjectDoesNotExist:
            return False

    def check_visiblity(self, option, user):
        if not option:
            return
        elif self == user:
            visible = True
        else:
            visible = False

            if self.check_option(option, "Public"):
                visible = True
            elif self.check_option(option, "Friend's Friends"):
                if self.has_friends_friend(user):
                    visible = True
            elif self.check_option(option, "Friends"):
                if self.has_friend(user):
                    visible = True
            elif self.check_option(option, "Just Me"):
                visible = False
            elif self.check_option(option, "Off"):
                visible = False
            else:
                visible = True

        return visible

    def set_option(self,name,value):
        name = "option_%s" % name
        try:
            option = self.useroptions_set.get(name=name)
            option.value = value
            option.save()
        except ObjectDoesNotExist:
            self.useroptions_set.create(name=name,value=value)

    def new_messages(self):
        return self.message_to.filter(viewed=False).count()

    def new_notifcations(self):
        return self.notification_set.filter(read=False) \
                .exclude(type='MC') \
                .exclude(type='MF') \
                .exclude(type='MS') \
                .exclude(type='MM') \
                .exclude(type='FM') \
                .exclude(type='MP') \
                .count()

    def add_follower(self, person):
        relationship, created = Relationship.objects.get_or_create(
            from_user=self,
            to_user=person)
        return relationship

    def add_following(self, person):
        relationship, created = Relationship.objects.get_or_create(
            from_user=person,
            to_user=self)
        return relationship

    def get_following_active(self, user=None):
        following = Relationship.objects.filter(to_user=self, status=1)
        if user:
            following = following.exclude(from_user=user.id)
        following = [x.from_user for x in following if x.from_user not in self.get_blocked()]
        return following

    def get_followers_active(self, user=None):
        followers = Relationship.objects.filter(from_user=self, status=1)
        if user:
            followers = followers.exclude(to_user=user.id)
        followers = [x.to_user for x in followers if x.to_user not in self.get_blocked()]
        return followers

    def get_following_blocked(self):
        following = Relationship.objects.filter(to_user=self, status=0)
        following = [x.from_user for x in following]
        return following

    def get_followers_blocked(self):
        followers = Relationship.objects.filter(from_user=self, status=0)
        followers = [x.to_user for x in followers]
        return followers

    def get_following_count(self, user=None):
        if not user:
            count = Relationship.objects.filter(to_user=self, status=1).exclude(from_user__in=self.get_blocked()).count()
        else:
            count = Relationship.objects.filter(to_user=self, status=1).exclude(from_user__in=self.get_blocked()).\
                    exclude(from_user__id=user.id).count()
        return count

    def get_followers_count(self, user=None):
        if not user:
            count = Relationship.objects.filter(from_user=self, status=1).exclude(to_user__in=self.get_blocked()).count()
        else:
            count = Relationship.objects.filter(from_user=self, status=1).exclude(to_user__in=self.get_blocked()).\
                    exclude(to_user__id=user.id).count()
        return count

    def in_followers(self,user):
        followers = Relationship.objects.filter(from_user=self)
        followers = [x.to_user for x in followers]
        if user in followers:
            return True
        else:
            return False

    def remove_following(self, user):
        Relationship.objects.filter(
                from_user=user,
                to_user=self).delete()
        return

    def block_following(self, user):
        following = Relationship.objects.filter(
                from_user=user,
                to_user=self)
        following.update(status = 0)
        return

    def block_follower(self, user):
        follower = Relationship.objects.filter(
                from_user=self,
                to_user=user)
        follower.update(status = 0)
        return

    def activate_following(self, user):
        following = Relationship.objects.filter(
                from_user=user,
                to_user=self)
        following.update(status = 1)
        return

    def activate_follower(self, user):
        following = Relationship.objects.filter(
                from_user=self,
                to_user=user)
        following.update(status = 1)
        return

    def get_loved(self):
        return self.pages_loved.all()

    @models.permalink
    def get_absolute_url(self):
        return ('profile.views.profile', [str(self.username)])

    def _get_full_name(self):
        return self.optional_name or '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def get_full_name(self):
        "Returns the person's full name."
        return self.full_name


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        uprofile = UserProfile(user_ptr_id=instance.pk)
        uprofile.__dict__.update(instance.__dict__)
        uprofile.save()
post_save.connect(create_user_profile, sender=User)


class UserImage(models.Model):
    image = ImageWithThumbField(upload_to="uploads/images",
        storage=ImageStorage())
    owner = models.ForeignKey('UserProfile', related_name='my_images')
    profiles = models.ManyToManyField('UserProfile', related_name='all_images',
        through='UserImages')

    def __unicode__(self):
        return self.image.name


# Need argument update_fields for thumb, New in Django 1.5
def create_user_image(sender, instance, created, **kwargs):
    if created:
        from PIL import Image
        
        try:
            pil_object = Image.open(instance.image.path)
            w, h = pil_object.size
            x, y = 0, 0
            if w > h:
                x, y, w, h = int((w-h)/2), 0, h, h
            elif h > w:
                x, y, w, h = 0, int((h-w)/2), w, w
            new_pil_object = pil_object.crop((x, y, x+w, y+h))
            new_pil_object.save(instance.image.thumb_path)
            # The best way definition content_type is magic, may be use her?
            # http://pypi.python.org/pypi/python-magic/
            #new_pil_object.save(instance.image.thumb_path,
            #    format=Image.EXTENSION.get(os.path.splitext(instance.image.path)[1], 'JPEG'))
        except:
            pass
post_save.connect(create_user_image, sender=UserImage)


def delete_user_image(sender, instance, **kwargs):
    # remove all user_image_tag linked with current image
    UserImageTag.objects.filter(image=instance).delete()
    # remove image files from fs
    picture = instance.image
    picture.storage.delete(picture.thumb_path)
    picture.delete(save=False)
pre_delete.connect(delete_user_image, sender=UserImage)


import post.models
class UserImagesQuerySet(post.models.QuerySet):
    DEFAULT_ROW_SIZE = 4

    def total_rows(self):
        from math import ceil
        return int(ceil(self.count() / float(self.DEFAULT_ROW_SIZE)))

    def get_rows(self, start, count, size=DEFAULT_ROW_SIZE):
        qs = self.order_by('-activity', '-rating')
        images = qs[start*size:(start+count)*size]
        rows = []
        for i in xrange(0, len(images), size):
            rows.append({
                'index': start + i/size,
                'rows': images[i:i+size],
            })
        return rows

    def get_row(self, start, size=DEFAULT_ROW_SIZE):
        return self.get_rows(start, 1)[0]



class UserImages(models.Model):
    image = models.ForeignKey('UserImage')
    profile = models.ForeignKey('UserProfile')
    rating = models.IntegerField(blank=True, null=True)
    activity = models.BooleanField(default=False)

    objects = UserImagesQuerySet.as_manager()

    def __unicode__(self):
        return '%s link to %s' % (self.image, self.profile)



def create_user_images(sender, instance, created, **kwargs):
    if created:
        instance.rating = instance.id
        instance.save()
post_save.connect(create_user_images, sender=UserImages)


def delete_user_images(sender, instance, **kwargs):
    # set default photo if current image activity
    if instance.activity:
        profile = instance.profile
        profile.photo = [field.default
            for field in UserProfile._meta.fields if field.name == 'photo'
        ][0]
        profile.save()
    # check count link to this image, and remove it if link count is 0
    if UserImages.objects.filter(image=instance.image).count() == 0:
        instance.image.delete()
post_delete.connect(delete_user_images, sender=UserImages)


class UserImageTag(models.Model):
    image = models.ForeignKey('UserImage')
    profile = models.ForeignKey('UserProfile', blank=True, null=True)
    page = models.CharField(max_length='100', blank=True, null=True)
    coords = CoordsField()
    is_delete = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s in %s' % (self.image, self.profile)



class Relationship(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='from_people')
    to_user = models.ForeignKey(UserProfile, related_name='to_people')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length='1', choices=RELATIONSHIP_STATUSES, default=1)

    def save(self, *args, **kwargs):
        follow = False
        if self.from_user.check_option('follow',"Public"):
            follow = True
        elif self.from_user.check_option('follow',"Friend's Friends"):
            if self.from_user.has_friends_friend(self.to_user):
                follow = True
        elif self.from_user.check_option('follow',"Off"):
            pass
        else:
            follow = True
        if (follow):
            super(Relationship, self).save(*args, **kwargs)
        return follow


class UserOptions(models.Model):
    name = models.CharField(max_length='100')
    value = models.CharField(max_length='100')
    user = models.ForeignKey(UserProfile)


