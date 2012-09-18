from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.query import Q
from post.tasks import AddFriendToFeed
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from itertools import chain

FILTER_TYPE = (
    ('F', 'Friend Feed'),
    ('T', 'Tag Feed'),
    ('P', 'Pages Feed'),
    ('A', 'Public Feed'),
)

RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 2
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
        Notification(user=self.from_user, type='FA', other_user=self.to_user, content_object = self).save()
        FriendPost(user=self.from_user, friend=self.to_user, user_to=self.to_user).save()
        #AddFriendToFeed.delay(self.from_user, self.to_user)
        #AddFriendToFeed.delay(self.to_user, self.from_user)
        self.delete()

    # Decline the friend request
    def decline(self):
        self.delete()

class UserProfile(User):
    # Logic is if a friend is in the 'friends' collection then they are verified.
    # If there is an active FriendRequest then it's still pending.
    friends = models.ManyToManyField('self', related_name='friends')
    photo = models.ImageField(upload_to="uploads/images", verbose_name="Please Upload a Photo Image", default='images/noProfilePhoto.png')
    filters = models.CharField(max_length='10', choices=FILTER_TYPE, default="F")
    followers =  models.ManyToManyField('self', related_name='following', symmetrical=False, through="Relationship")

    def has_friend(self, user):
        return self.friends.filter(id=user.id).count() > 0

    def has_friends_friend(self, user):
        for friend in self.friends.all():
            if self.friends.filter(id=friend.id).count() > 0 or friend == user:
                return True
        return False

    def has_friend_request(self, user):
        return FriendRequest.objects.filter(Q(from_user=self, to_user=user) | Q(to_user=self, from_user=user)).count() > 0

    # Returns a queryset for all news items this user can see in date order.
    def get_news(self):
        from post.models import NewsItem
        #return NewsItem.objects.filter(user=self, hidden=False).order_by('date').reverse()
        #User can see all public messages,
        #not only his
        return NewsItem.objects.filter(hidden=False).order_by('date').reverse()
    def get_messages(self):
        from post.models import NewsItem
        #return NewsItem.objects.filter(post__user_to__in=self.friends.all()).exclude(post__user=self).order_by('date').reverse()
        user_list = self.friends.all()
        following = self.following.all()
        user_list = list(set(list(chain(user_list,following))))
        return NewsItem.objects.filter(user__in=user_list).exclude(post__user=self).order_by('date').reverse()

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
    def check_visiblity(self,option,user):
        if not option:
            return
        else:
            visible = False

            if self.check_option(option,"Public"):
                visible = True
            elif self.check_option(option,"Friend's Friends"):
                if self.has_friends_friend(user):
                    visible = True
            elif self.check_option(option,"Friends"):
                if self.has_friend(user):
                    visible = True
            elif self.check_option(option,"Just Me"):
                visible = False
            elif self.check_option(option,"Off"):
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
        return self.message_to.filter(read=False).count()
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
    def in_followers(self,user):
        if user in self.followers.all():
            return True
        else:
            return False
    def remove_following(self, user):
        Relationship.objects.filter(
                from_user=user,
                to_user=self).delete()
        return


    @models.permalink
    def get_absolute_url(self):
        return ('profile.views.profile', [str(self.username)])

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

class Relationship(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='from_people')
    to_user = models.ForeignKey(UserProfile, related_name='to_people')
    date = models.DateTimeField(auto_now_add=True)

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

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        up = UserProfile(user_ptr_id=instance.pk)
        up.__dict__.update(instance.__dict__)
        up.save()
post_save.connect(create_user_profile, sender=User)
