from itertools import chain

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.db.models.signals import post_save, pre_delete
from django.db.models.query import Q
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import datetime as dateclass

from images.fields import ImageWithThumbField


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

IN_RELATIONSHIP = (
    ('S', 'single'),
    ('D', 'dating'),
    ('E', 'engaged'),
    ('M', 'married'),
)


class RelationRequest(models.Model):
    from_user = models.ForeignKey('UserProfile', related_name='relation_from')
    to_user = models.ForeignKey('UserProfile', related_name='relation_to')
    date = models.DateTimeField(auto_now_add=True)
    type = models.TextField(max_length=1, choices=IN_RELATIONSHIP)

    def accept(self):
        self.from_user.relationtype = self.type
        self.from_user.in_relationship = self.to_user
        self.to_user.relationtype = self.type
        self.to_user.in_relationship = self.from_user
        # if already have relationships
        #UserProfile.objects.filter(in_relationship=self.to_user)
        #UserProfile.objects.filter(in_relationship=self.from_user)
        try:
            self.to_user.save()
            self.from_user.save()
        except:
            # somebody is lying here <_<
            pass
        self.delete()

    def decline(self):
        self.delete()

    def get_relation_type(self):
        relation = self.type
        if relation:
            for rlt in IN_RELATIONSHIP:
                if rlt[0] == relation:
                    return rlt[1]
        return relation


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
        Notification(user=self.from_user, type='FA', other_user=self.to_user, content_object=self).save()
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
    cover_photo = models.ImageField(upload_to="uploads/images",
                                    default='uploads/images/bg_cover.png')
    images_quote = models.CharField(max_length=200,
                                    default=settings.IMAGES_DEFAULT_QUOTE)
    images_quote_author = models.CharField(
        max_length=20,
        default=settings.IMAGES_DEFAULT_QUOTE_AUTHOR)
    filters = models.CharField(max_length=10, choices=FILTER_TYPE,
                               default="F")
    followers = models.ManyToManyField('self', related_name='following', symmetrical=False, through="Relationship")
    optional_name = models.CharField(max_length=200, default="")
    timezone = models.CharField(max_length=200, blank=True)
    in_relationship = models.OneToOneField('self', null=True, blank=True)
    relationtype = models.CharField(max_length=1, choices=IN_RELATIONSHIP, blank=True)
    bio_text = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)

    def get_thumb(self):
        return "/%s" % self.photo.thumb_name

    def get_cover_photo(self):
        return "/%s" % self.cover_photo.url

    def get_default_cover_photo(self):
        return "/%s" % self.cover_photo.field.default

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
        if mutual_friends:
            mutual_friends = sorted(mutual_friends, key=lambda u: u.get_full_name())

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

    def get_unrelated_friends(self):
        blocked_ids = [x.id for x in self.get_blocked_self()]
        friends = self.friends.exclude(id__in=blocked_ids).exclude(relationtype__in=('D', 'E', 'M'))
        return friends

    def get_relation(self):
        relation = self.relationtype
        return relation

    def get_relation_type(self):
        relation = self.relationtype
        if relation:
            for rlt in IN_RELATIONSHIP:
                if rlt[0] == relation:
                    return rlt[1]
        return relation

    def has_pending_notifications(self):
        nots = RelationRequest.objects.filter(from_user=self).count()
        return nots

    def get_bio_info(self):
        return self.bio_text

    def get_birth_date(self):
        return self.birth_date

    def get_website(self):
        url = self.url
        if url:
            link = '<a class="website_link" title="%s" target="_blank" rel="nofollow" href="%s">%s</a>' % (url, url, url)
            return link
        return url

    def get_related_person(self):
        return self.in_relationship

    def has_friend_request(self, user):
        return FriendRequest.objects.filter(Q(from_user=self, to_user=user) | Q(to_user=self, from_user=user)).count() > 0

    def in_hidden(self, user):
        return self.hidden.filter(id=user.id).count() > 0

    def get_blocked(self):
        blocked = [x for x in self.blocked.all()]
        blocked_from = [x for x in self.blocked_from.all()]
        blocked_all = list(set(list(chain(blocked, blocked_from))))
        return blocked_all

    def get_blocked_ids(self):
        blocked = [x.id for x in self.blocked.all()]
        blocked_from = [x.id for x in self.blocked_from.all()]
        blocked_all = list(set(list(chain(blocked, blocked_from))))
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
    def get_messages(self, filters=None):
        from post.models import NewsItem
        filters = filters or self.filters.split(',')
        # Friends
        if 'F' in filters:
            hidden_list = [x.id for x in self.hidden.all()]
            user_list = self.friends.all().exclude(id__in=hidden_list)
        else:
            user_list = []
        # Following
        if 'W' in filters:
            following = self.get_following_active()
            following = [x for x in following if x.check_visiblity('follow', self)]
        else:
            following = []
        # Blocked
        if self.get_blocked():
            blocked = [x for x in self.get_blocked()]
        else:
            blocked = []
        user_list = list(set(list(chain(user_list, following))))
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

    def check_option(self, name, value=None):
        name = "option_%s" % name
        try:
            option = self.useroptions_set.get(name=name)
            if value:
                if option.value == value:
                    return True
                else:
                    return False
            else:
                if option.value == 'True':
                    return True
                elif option.value == 'False':
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

    def set_option(self, name, value):
        name = "option_%s" % name
        try:
            option = self.useroptions_set.get(name=name)
            option.value = value
            option.save()
        except ObjectDoesNotExist:
            self.useroptions_set.create(name=name, value=value)

    def remove_option(self, name):
        name = "option_%s" % name
        try:
            option = self.useroptions_set.get(name=name)
            option.delete()
            return True
        except ObjectDoesNotExist:
            return False

    def find_options(self, name, page=None):
        name = "option_%s" % name
        options = self.useroptions_set.filter(name__startswith=name)
        if page:
            page_name = "__%s" % (page.id)
            options = self.useroptions_set.filter(name__startswith=name, name__endswith=page_name)
        return options

    def new_messages(self):
        #messages = self.message_to.filter(viewed=False).count()
        messages = self.message_to.filter(viewed=False).aggregate(Count('user', distinct='True'))
        return messages.get('user__count')

    def new_notifcations(self):
        """
        notifications_count = self.notification_set.filter(read=False) \
                .exclude(type__in=['MC', 'MI', 'MF', 'MS', 'MD', 'MM', 'FM', 'MP']) \
                .count()
        """
        notifications_count = self.notification_set.filter(read=False,
                                                           hidden=False) \
            .count()
        return notifications_count

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

    def in_followers(self, user):
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
        following.update(status=0)
        return

    def block_follower(self, user):
        follower = Relationship.objects.filter(
            from_user=self,
            to_user=user)
        follower.update(status=0)
        return

    def activate_following(self, user):
        following = Relationship.objects.filter(
            from_user=user,
            to_user=self)
        following.update(status=1)
        return

    def activate_follower(self, user):
        following = Relationship.objects.filter(
            from_user=self,
            to_user=user)
        following.update(status=1)
        return

    def get_loved(self):
        return self.pages_loved.all()

    def get_loved_posts(self):
        return self.posts_loved.all()

    def get_pages(self):
        return self.pages.all()

    def get_favourite_pages(self):
        pages = self.pages_favourites.order_by('pagefavourites__position')
        return pages

    def get_admin_pages(self):
        return self.pages_admin.all()

    def get_community_pages(self):
        pages = self.get_admin_pages()
        comm_pages = [page for page in pages if self.check_option('pages_community__%s' % page.id)]
        return comm_pages

    def get_community_pages_friends(self, friendpage=None):
        pages = self.get_admin_pages()
        comm_pages = [page for page in pages if self.check_option('pages_community__%s' % page.id)]
        if friendpage:
            friends = []
            for page in comm_pages:
                if friendpage in page.get_friends():
                    friends.append(page)
        else:
            friends = []
            for page in comm_pages:
                for friend in page.get_friends():
                    if friend not in friends:
                        friends.append(friend)
        return friends

    def get_community_pages_count(self, page=None):
        pages = self.get_admin_pages()
        comm_pages = [one_page for one_page in pages if self.check_option('pages_community__%s' % one_page.id)]
        if page:
            if page in comm_pages:
                comm_pages.remove(page)
            topage_requests = [one_page.from_page for one_page in page.get_requests()]
            page_friends = page.get_friends()
            sum_pages = set(chain(page_friends, topage_requests))
            comm_pages = [one_page for one_page in comm_pages if one_page not in sum_pages]
        return len(comm_pages)

    def get_user_roles_for(self, page):
        roles = ['P']
        if self in page.get_admins():
            roles.append('A')
        if self.membership_set.filter(page=page, type='EM', is_confirmed=True).count():
            roles.append('E')
        if self.membership_set.filter(page=page, type='VL', is_confirmed=True).count():
            roles.append('E')
        if self.membership_set.filter(page=page, type='IN', is_confirmed=True).count():
            roles.append('I')
        return roles

    def is_employee_for(self, page):
        qry = self.membership_set.filter(page=page, type='EM', is_confirmed=True).count()
        if qry:
            return True
        return False

    def is_volunteer_for(self, page):
        qry = self.membership_set.filter(page=page, type='VL', is_confirmed=True).count()
        if qry:
            return True
        return False

    def is_intern_for(self, page):
        qry = self.membership_set.filter(page=page, type='IN', is_confirmed=True).count()
        if qry:
            return True
        return False

    def posted_review_for(self, page):
        reviews = page.feedback_posts.filter(user=self).order_by('-date')
        if reviews.count():
            now = timezone.now()
            delta = dateclass.timedelta(days=7)
            review = reviews[0]
            offset = review.date + delta
            if  offset > now:
                remain = offset - now
                return remain.days
        return False

    def is_lcustomer_for(self, page):
        return self.customer.filter(page=page, section='L').count()

    def is_customer_for(self, page):
        return self.customer.filter(page=page, section='B').count()

    def get_love_stripe_id(self):
        return self.customer.get(section='L').stripe_id

    def get_stripe_id(self):
        return self.customer.get(section='B').stripe_id

    def get_current_bid_for(self, page):
        bids = self.bids.filter(page=page, status=1).order_by('-amount')
        if bids:
            bids = bids[0]
        return bids

    def get_love_last_4(self, page):
        if self.is_lcustomer_for(page):
            customer = self.customer.get(page=page, section='L')
            return customer.get_last_four()
        else:
            return False

    def get_last_4(self, page):
        if self.is_customer_for(page):
            customer = self.customer.get(page=page, section='B')
            return customer.get_last_four()
        else:
            return False

    def get_love_card_type_for(self, page):
        if self.is_lcustomer_for(page):
            customer = self.customer.get(page=page, section='L')
            return customer.get_type()
        else:
            return False

    def get_card_type_for(self, page):
        if self.is_customer_for(page):
            customer = self.customer.get(page=page, section='B')
            return customer.get_type()
        else:
            return False

    def have_shared_topic_with(self, page):
        shared = self.topics_set.filter(tagged=page, privacy='I').count()
        return shared

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


class Relationship(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='from_people')
    to_user = models.ForeignKey(UserProfile, related_name='to_people')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=RELATIONSHIP_STATUSES, default=1)

    def save(self, *args, **kwargs):
        follow = False
        if self.from_user.check_option('follow', "Public"):
            follow = True
        elif self.from_user.check_option('follow', "Friend's Friends"):
            if self.from_user.has_friends_friend(self.to_user):
                follow = True
        elif self.from_user.check_option('follow', "Off"):
            pass
        else:
            follow = True
        if (follow):
            super(Relationship, self).save(*args, **kwargs)
        return follow


class UserOptions(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    user = models.ForeignKey(UserProfile)


def update_user_actions(sender, instance, using, **kwargs):
    # add loves limit to all loved pages 
    pages = instance.get_loved()
    for page in pages:
        page.loves_limit = page.loves_limit + 1
        page.save()
pre_delete.connect(update_user_actions, sender=UserProfile)
