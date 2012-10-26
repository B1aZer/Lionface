from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete, pre_save
from django.db.models.query import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError

from itertools import chain

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
        if self.to_user in self.from_user.get_following_active():
            #self.from_user.remove_following(self.to_user)
            self.from_user.block_following(self.to_user)
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
    photo = models.ImageField(upload_to="uploads/images", verbose_name="Please Upload a Photo Image", default='images/noProfilePhoto.png')
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

    def get_degree_for(self, user):
        from degrees.models import Degree
        deg = 'none'
        deg = Degree.objects.filter(from_user=self, to_user=user)
        if deg.count() > 0:
            deg = deg[0].distance
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

        if self == user:
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

    def activate_following(self, user):
        following = Relationship.objects.filter(
                from_user=user,
                to_user=self)
        following.update(status = 1)
        return

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

def update_user_profile(sender, instance, raw, using, **kwargs):
    try:
        current = sender.objects.get(id=instance.id)
    except sender.DoesNotExist:
        return
    if current.photo != instance.photo and current.photo.name != 'images/noProfilePhoto.png':
        current.photo.delete(save=False)
pre_save.connect(update_user_profile, sender=UserProfile)


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

def update_degree_of_separation(sender, instance, created, **kwargs):
    if created:
        import pdb;pdb.set_trace()
        # find all connections with final point equals to user
        # or find all in path
        # A -> B
        doses = Degree.objects.filter(to_user=instance.from_user).\
                exclude(from_user=instance.from_user, to_user=instance.to_user).\
                exclude(from_user=instance.to_user, to_user=instance.from_user)
                # exclude newly created
        if doses.count() > 0:
            for dos in doses:
                # make new connections with friended user
                if Degree.objects.filter(from_user=dos.from_user, to_user=instance.to_user).count() == 0:
                    conn = Degree(from_user=dos.from_user,\
                            to_user=instance.to_user,\
                            distance = dos.distance + 1)
                    conn.path = "%s,%s" % (dos.path, instance.to_user.id)
                    conn.save()
                elif Degree.objects.filter(from_user=instance.from_user, to_user=instance.to_user).count() > 0:
                    # checking if reverse exist
                    Degree.objects.get_or_create(from_user=instance.to_user,\
                            to_user=instance.from_user,\
                            distance = dos.distance + 1,\
                            path = "%s,%s" % (instance.to_user.id, dos.path))
                else:
                    # second run, firing above above
                    # reverse path would be different
                    # maybe check if reverse exist ?
                    Degree.objects.get_or_create(from_user=instance.to_user,\
                            to_user=instance.from_user,\
                            distance = dos.distance + 1,\
                            path = "%s,%s" % (dos.path, instance.from_user.id))
                    #post_save.connect(update_degree_of_separation, sender=Degree)

def update_degree_of_separation_on_delete(sender, instance, using, **kwargs):
    import pdb;pdb.set_trace()
    # 3 -> 2
    doses = Degree.objects.filter(from_user=instance.to_user).\
                exclude(from_user=instance.from_user, to_user=instance.to_user).\
                exclude(from_user=instance.to_user, to_user=instance.from_user)
    if doses.count() > 0:
            for dos in doses:
                # update connections with all connected users
                Degree(from_user=dos.from_user, to_user=instance.to_user).delete()
#post_delete.connect(update_degree_of_separation_on_delete, sender=Degree)

class UserOptions(models.Model):
    name = models.CharField(max_length='100')
    value = models.CharField(max_length='100')
    user = models.ForeignKey(UserProfile)


