from django.db import models
from account.models import UserProfile

from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_slug, URLValidator

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.db.models import F

from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings

from datetime import datetime
import datetime as dateclass
import logging
import cPickle

from images.fields import ImageWithThumbField
from django.db.models import Q, F

import operator

REQUEST_TYPE = (
        ('ER','Event Request'),
        ('PR','Page Request'),
        ('BN','Bidding Notifier'),
        ('BE','Bidding Error'),
        ('BB','Bidding Block'),
        ('BO','Bidding Out'),
)

PAGE_TYPE = (
        ('BS','Business Page'),
        ('NP','Nonprofit Page'),
)

MEMBERSHIP_TYPE = (
        ('VL','Volunteer'),
        ('IN','Intern'),
        ('EM','Employee'),
        ('MM','Member'),
)

PAGE_LOVE_STATUS = (
        ('A', 'Active'),
        ('Q', 'Queue'),
)

TOPIC_PRIVACY_SET = (
        ('P', 'Public'),
        ('I', 'Inter-Page'),
        ('H', 'In-House'),
)

TOPIC_MEMBERS_SET = (
        ('A','Admins'),
        ('E','Employees'),
        ('M','Members'),
        ('I','Interns'),
        ('V','Volunteers'),
)


class PageRequest(models.Model):
    from_page = models.ForeignKey('Pages', related_name='from_page')
    to_page = models.ForeignKey('Pages', related_name='to_page')
    event = models.ForeignKey('agenda.Events', related_name='from_event', null=True, blank=True)
    type = models.CharField(max_length=2, choices=REQUEST_TYPE, default='PR')
    date = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def accept(self):
        if self.type == 'PR':
            self.from_page.friends.add(self.to_page)
            self.is_accepted = True
            self.save()
        else:
            self.event.tagged.add(self.to_page)
            self.is_accepted = True
            self.save()

    def hide(self):
        self.is_hidden = True
        self.save()

    def decline(self):
        self.delete()



class PagePositions(models.Model):
    to_page = models.ForeignKey('Pages', related_name='posto_page')
    from_page = models.ForeignKey('Pages', related_name='postfrom_page')
    position = models.IntegerField(blank = True, null = True)


class PageLoves(models.Model):
    page = models.ForeignKey('Pages')
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=PAGE_LOVE_STATUS, default='A')


class PageFavourites(models.Model):
    page = models.ForeignKey('Pages')
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(blank=True, null=True)

def change_page_postion(sender, instance, created, **kwargs):
    if created:
        #getting max position
        max_pos = PageFavourites.objects.filter(
            user=instance.user).order_by("-position")[0].position
        if max_pos is not None:
            instance.position = max_pos + 1
            instance.save()
        else:
            instance.position = 0
            instance.save()
post_save.connect(change_page_postion, sender=PageFavourites)

def change_page_postion_ondelete(sender, instance, **kwargs):
    pages = PageFavourites.objects.filter(
        position__gt=instance.position, user=instance.user)
    if pages.count() > 0:
        pages.update(position=F('position') - 1)
post_delete.connect(change_page_postion_ondelete, sender=PageFavourites)


class Pages(models.Model):
    name = models.CharField(max_length=200)
    friends = models.ManyToManyField('self', related_name='friends')
    loves = models.IntegerField(default=0)
    loves_limit = models.IntegerField(default=100)
    username = models.CharField(max_length=200, validators=[validate_slug], unique=True)
    url = models.URLField(max_length=2000, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    user = models.ForeignKey(UserProfile, related_name='pages')
    users_loved = models.ManyToManyField(UserProfile, through='PageLoves', related_name='pages_loved', null=True, blank=True)
    users_favourites = models.ManyToManyField(UserProfile, through='PageFavourites', related_name='pages_favourites', null=True, blank=True)
    admins = models.ManyToManyField(UserProfile, related_name='pages_admin', null=True, blank=True)
    type = models.CharField(max_length=2, choices=PAGE_TYPE)
    category = models.CharField(max_length=100, default='Undefined')
    cover_photo = models.ImageField(upload_to="uploads/images", default='uploads/images/noCoverImage.png')
    photo = ImageWithThumbField(upload_to="uploads/images", default='uploads/images/noProfilePhoto.png')
    # members
    has_employees = models.BooleanField(default=False)
    text_employees = models.TextField(blank=True)
    has_interns = models.BooleanField(default=False)
    text_interns = models.TextField(blank=True)
    has_volunteers = models.BooleanField(default=False)
    text_volunteers = models.TextField(blank=True)
    has_members = models.BooleanField(default=False)
    text_members = models.TextField(blank=True)
    members = models.ManyToManyField(UserProfile, related_name="member_of", through='Membership')
    # calendar
    post_update = models.BooleanField(default=False)
    # deletion
    for_deletion = models.DateTimeField(null=True, blank=True)
    # bidding
    featured = models.BooleanField(default=False)
    is_disabled = models.DateTimeField(null=True, blank=True)
    exempt = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __unicode__(self):
        return self.username

    def __repr__ (self):
        return '<Page %s> %s: %s' % (self.id, self.username, self.loves)

    def get_thumb(self):
        return "/%s" % self.photo.thumb_name

    def get_loves(self):
        loves = self.users_loved.filter(pageloves__status='A').count()
        return loves

    def get_lovers(self):
        lovers = self.users_loved.all()
        return lovers

    def get_lovers_count(self):
        return self.get_lovers().count()

    def get_lovers_active(self):
        lovers = self.users_loved.filter(pageloves__status='A')
        return lovers

    def get_lovers_pending(self):
        lovers = self.users_loved.filter(pageloves__status='Q')
        return lovers

    def get_lovers_active_count(self):
        lovers = self.get_lovers_active().count()
        return lovers

    def get_lovers_pending_count(self):
        lovers = self.get_lovers_pending().count()
        return lovers

    def get_lovers_public(self):
        lovers = self.get_lovers()
        lovers = [lover for lover in lovers if not lover.check_option('loves','Private')]
        return lovers

    def get_lovers_public_count(self):
        lovers = self.get_lovers()
        lovers = [lover for lover in lovers if not lover.check_option('loves','Private')]
        return len(lovers)

    def get_lovers_private_count(self):
        lovers = self.get_lovers()
        lovers = [lover for lover in lovers if lover.check_option('loves','Private')]
        return len(lovers)

    def get_lovers_ordered(self):
        # limit to 7x10 rows
        lovers = self.get_lovers_public()[:70]
        lovers = sorted(lovers, key=lambda s: s.get_followers_count(), reverse=True)
        return lovers

    def get_page_loves_limit(self):
        return self.loves_limit

    def get_posts(self):
        return self.posts.all()

    def get_feedback(self):
        return self.feedback_posts.all()

    def get_admins(self):
        return self.admins.all()

    def get_community_admins(self):
        comm_admins = [admin
                for admin in self.admins.all()
                    if admin.check_option('pages_community__%s' % self.id)]
        return comm_admins

    def get_requests(self):
        return self.to_page.filter(is_hidden=False, is_accepted=False, type='PR')

    def get_requests_count(self):
        return self.get_requests().count()

    def get_accepted_requests(self):
        return self.from_page.filter(is_hidden=False, is_accepted=True, type='PR')

    def get_events_requests(self):
        return self.to_page.filter(is_hidden=False, is_accepted=False, type='ER')

    def get_bidding_notifiers(self):
        return self.to_page.filter(is_hidden=False, is_accepted=False, type__in=('BN','BE','BB','BO'))

    def get_friends(self):
        return self.friends.all()

    def get_business_friends(self):
        bs_pages = self.friends.filter(type='BS')
        bs_pages = sorted(bs_pages, key= lambda s: self.get_position_for(s))
        return bs_pages

    def get_nonprofit_friends(self):
        np_pages = self.friends.filter(type='NP')
        np_pages = sorted(np_pages, key= lambda s: self.get_position_for(s))
        return np_pages

    def get_friends_count(self):
        return self.friends.count()

    def get_position_for(self, page):
        try:
            obj = PagePositions.objects.get(to_page=self, from_page=page)
            return obj.position
        except:
            return 0

    def get_community_requests(self):
        return Membership.objects.filter(page=self, is_confirmed=False)

    def get_community_requests_past(self):
        requests = Membership.objects.filter(page=self, is_confirmed=False, is_present=False)
        return requests

    def get_community_requests_present(self):
        return Membership.objects.filter(page=self, is_confirmed=False, is_present=True)

    def get_community_requests_count(self):
        return self.get_community_requests().count()

    def get_community_requests_count_new(self):
        return self.get_community_requests().filter(is_new=True).count()

    def get_community_requests_emloyees(self):
        return Membership.objects.filter(page=self, type='EM', is_confirmed=False)

    def get_community_requests_emloyees_past(self, update=True):
        requests = Membership.objects.filter(page=self, type='EM', is_confirmed=False, is_present=False)
        pickle_str = cPickle.dumps(requests)
        if update:
            requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_emloyees_past_count(self):
        return self.get_community_requests_emloyees_past(False).count()

    def get_community_requests_emloyees_present(self):
        requests = Membership.objects.filter(page=self, type='EM', is_confirmed=False, is_present=True)
        pickle_str = cPickle.dumps(requests)
        requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_emloyees_present_count(self):
        return self.get_community_requests_emloyees_present().count()

    def get_community_requests_members(self):
        return Membership.objects.filter(page=self, type='MM', is_confirmed=False)

    def get_community_requests_members_past(self, update=True):
        requests = Membership.objects.filter(page=self, type='MM', is_confirmed=False, is_present=False)
        pickle_str = cPickle.dumps(requests)
        if update:
            requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_members_past_count(self):
        return self.get_community_requests_members_past(False).count()

    def get_community_requests_members_present(self):
        requests = Membership.objects.filter(page=self, type='MM', is_confirmed=False, is_present=True)
        pickle_str = cPickle.dumps(requests)
        requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_members_present_count(self):
        return self.get_community_requests_members_present().count()

    def get_community_requests_interns(self):
        return Membership.objects.filter(page=self, type='IN', is_confirmed=False)

    def get_community_requests_interns_past(self, update=True):
        requests = Membership.objects.filter(page=self, type='IN', is_confirmed=False, is_present=False)
        pickle_str = cPickle.dumps(requests)
        if update:
            requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_interns_past_count(self):
        return self.get_community_requests_interns_past(False).count()

    def get_community_requests_interns_present(self):
        requests = Membership.objects.filter(page=self, type='IN', is_confirmed=False, is_present=True)
        pickle_str = cPickle.dumps(requests)
        requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_interns_present_count(self):
        return self.get_community_requests_interns_present().count()

    def get_community_requests_volunteers(self):
        return Membership.objects.filter(page=self, type='VL', is_confirmed=False)

    def get_community_requests_volunteers_past(self, update=True):
        requests = Membership.objects.filter(page=self, type='VL', is_confirmed=False, is_present=False)
        pickle_str = cPickle.dumps(requests)
        if update:
            requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_volunteers_past_count(self):
        return self.get_community_requests_volunteers_past(False).count()

    def get_community_requests_volunteers_present(self):
        requests = Membership.objects.filter(page=self, type='VL', is_confirmed=False, is_present=True)
        pickle_str = cPickle.dumps(requests)
        requests.update(is_new=False)
        requests = cPickle.loads(pickle_str)
        return requests

    def get_community_requests_volunteers_present_count(self):
        return self.get_community_requests_volunteers_present().count()

    def get_members(self):
        members = Membership.objects.filter(page=self, is_confirmed=True)
        return members

    def get_emloyees_ordered(self):
        members = Membership.objects.filter(page=self, type='EM', is_confirmed=True)[:70]
        users = [member.get_user() for member in members if not member.get_user().check_option('vie_pages','Private')]
        users = sorted(users, key=lambda s: s.get_followers_count(), reverse=True)
        return users

    def get_interns_ordered(self):
        members = Membership.objects.filter(page=self, type='IN', is_confirmed=True)[:70]
        users = [member.get_user() for member in members if not member.get_user().check_option('vie_pages','Private')]
        users = sorted(users, key=lambda s: s.get_followers_count(), reverse=True)
        return users

    def get_members_ordered(self):
        members = Membership.objects.filter(page=self, type='MM', is_confirmed=True)[:70]
        users = [member.get_user() for member in members if not member.get_user().check_option('vie_pages','Private')]
        users = sorted(users, key=lambda s: s.get_followers_count(), reverse=True)
        return users

    def get_volunteers_ordered(self):
        members = Membership.objects.filter(page=self, type='VL', is_confirmed=True)[:70]
        users = [member.get_user() for member in members if not member.get_user().check_option('vie_pages','Private')]
        users = sorted(users, key=lambda s: s.get_followers_count(), reverse=True)
        return users

    def get_emloyees_ordered_count(self):
        members = Membership.objects.filter(page=self, type='EM', is_confirmed=True).count()
        return members

    def get_members_ordered_count(self):
        members = Membership.objects.filter(page=self, type='MM', is_confirmed=True).count()
        return members

    def get_interns_ordered_count(self):
        members = Membership.objects.filter(page=self, type='IN', is_confirmed=True).count()
        return members

    def get_volunteers_ordered_count(self):
        members = Membership.objects.filter(page=self, type='VL', is_confirmed=True).count()
        return members

    def show_membership(self, user):
        membership = Membership.objects.filter(page=self, user=user, is_confirmed=True)
        return membership

    def show_connections(self, user):
        membership = Membership.objects.filter(page=self, user=user)
        return membership

    def check_employees(self):
        return self.has_employees

    def check_interns(self):
        return self.has_interns

    def check_members(self):
        return self.has_members

    def check_volunteers(self):
        return self.has_volunteers

    def get_rating(self):
        overall_rating = 0
        rating_posts = self.feedback_posts.all()
        rating_count = rating_posts.count()
        rating_all = [post.rating for post in rating_posts]
        for rate in rating_all:
            overall_rating += rate
        if rating_count > 0:
            overall_rating = overall_rating * 1.0 /rating_count
        overall_rating = "{0:.1f}".format(overall_rating)
        return overall_rating

    def get_deletion_offset(self):
        if self.for_deletion:
            dif = timezone.now() - self.for_deletion
            return abs(dif.days)
        else:
            return False

    def get_disabled_time(self):
        if self.is_disabled:
            dif = timezone.now() - self.is_disabled
            return abs(dif.days)
        else:
            return False

    def update_option(self):
        return self.post_update

    def get_max_bid(self):
        bids = self.bids.filter(status=1).order_by('-amount')
        if bids:
            bids = bids[0]
        return bids

    def get_max_bid_value(self):
        bid = self.get_max_bid()
        if bid:
            bid = bid.amount
        else:
            bid = 10
        return bid

    def get_stripe_id(self):
        return self.customer.get().stripe_id

    def get_love_stripe_id(self, user):
        try:
            customer = self.customer.get(user=user, section='L')
            return customer.stripe_id
        except:
            return False

    def get_stripe_id_for(self, user):
        try:
            customer = self.customer.get(user=user, section='B')
            return customer.stripe_id
        except:
            return False

    def get_lcustomer_for(self, user):
        try:
            customer = self.customer.get(user=user, section='L')
            return customer
        except:
            return False

    def get_customer_for(self, user):
        try:
            customer = self.customer.get(user=user, section='B')
            return customer
        except:
            return False

    def get_topics(self):
        topics = self.tagged_in_topics.all()
        paginator = Paginator(topics, 7)
        topics = paginator.page(1)
        return topics

    def get_topics_for(self, user):
        # OPTIMIZE: query filter like
        now = timezone.now()
        delta = dateclass.timedelta(days=365 * 5)
        old_date = now - delta

        def sort_by_both_values(topic):
            date1 = topic.get_last_post_date()
            date2 = topic.get_last_comment_date()
            if date1 and date2:
                if date1 > date2:
                    return date1
                elif date2 > date1:
                    return date2
                else:
                    return date1
            elif date1:
                return date1
            # dummy return
            return old_date

        priv_topics = []
        topics = self.tagged_in_topics.all()
        if user.is_anonymous():
            roles = ['P']
        else:
            roles = user.get_user_roles_for(self)
        for topic in topics:
            for role in roles:
                if role in topic.members \
                        or topic.privacy == 'P' \
                        or (topic.privacy == 'I' and user == topic.user):
                    priv_topics.append(topic)
                    break
                else:
                    pass
        # this will sort by 1st then second (we need by both)
        # sorted by 2 dates (tuples for None compare)
        """
        priv_topics = sorted(priv_topics, key=lambda s: (
                (s.get_last_post_date() is not None, s.get_last_post_date()),
                (s.get_last_comment_date() is not None, s.get_last_comment_date())
                ), reverse = True
            )
        """
        priv_topics = sorted(priv_topics, key=sort_by_both_values, reverse = True)
        return priv_topics

    def get_popular_topics(self, user=None):
        # owned topics
        argument_list = [Q(**{'privacy__icontains':'P'} )]
        if user:
            roles = user.get_user_roles_for(self)
            for role in roles:
                argument_list.append( Q(**{'members__icontains':role} ) )
        topics = self.topics_set.filter(reduce(operator.or_, argument_list))
        def popular_sort(topic):
            # (1 point per view) +
            # total posts (1 point) +
            # total comments (.5 point)
            value = 0
            value = value + topic.get_views_count()
            value = value + topic.get_posts_count()
            value = value + (topic.get_comment_count() * 0.5)
            return value
        topics = sorted(topics, key=popular_sort, reverse=True)
        topics = topics[:4]
        return topics

    @models.permalink
    def get_absolute_url(self):
        if self.type == 'BS':
            return ('business-page', [str(self.username)])
        else:
            return ('nonprofit-page', [str(self.username)])

    def save(self, *args, **kwargs):
        """ Adding user to admins """
        super(Pages, self).save(*args, **kwargs)
        self.admins.add(self.user)
        self.user.set_option('pages_basics__%s' % self.id,True)
        self.user.set_option('pages_delete__%s' % self.id,True)
        self.user.set_option('pages_admins__%s' % self.id,True)
        self.user.set_option('pages_photos__%s' % self.id,True)
        self.user.set_option('pages_updates__%s' % self.id,True)
        self.user.set_option('pages_community__%s' % self.id,True)
        self.user.set_option('pages_calendar__%s' % self.id,True)
        self.user.set_option('pages_loves__%s' % self.id,True)


def change_friend_position(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    if action =='post_add':
        try:
            page = model.objects.get(id=pk_set.pop())
        except KeyError:
            # debugging
            logger = logging.getLogger(__name__)
            logger.error('Error in retrieving id')
            return
        friend = instance
        if friend.type == 'BS':
            position = len(page.get_business_friends())
            # for some reason page already in friend's list
            # adn we can't use pre_add here
        else:
            position = len(page.get_nonprofit_friends())

        if page.type == 'BS':
            friend_position = len(friend.get_business_friends()) - 1
        else:
            friend_position = len(friend.get_nonprofit_friends()) - 1

        position_obj = PagePositions(to_page=page, from_page=friend, \
                    position = position)
        # make the same for friend
        position_obj_friend = PagePositions(to_page=friend, from_page=page, \
                    position = friend_position)
        position_obj.save()
        position_obj_friend.save()
    if action =='post_remove':
        page = instance
        page_pos = None
        friend_pos = None
        try:
            friend = model.objects.get(id=pk_set.pop())
        except KeyError:
            logger = logging.getLogger(__name__)
            logger.error('Error in retrieving id')
            return
        try:
            page_pos = PagePositions.objects.get(to_page=page, from_page=friend)
            page_pos.delete()
        except:
            pass
        try:
            friend_pos = PagePositions.objects.get(to_page=friend, from_page=page)
            friend_pos.delete()
        except:
            pass
        # update positions
        if page_pos:
            PagePositions.objects.filter(to_page=page, \
                    position__gt=page_pos.position, \
                    from_page__type=friend.type)\
                .update(position=F('position') - 1)
        if friend_pos:
            PagePositions.objects.filter(to_page=friend,
                    position__gt=friend_pos.position,\
                    from_page__type=page.type)\
                .update(position=F('position') - 1)
m2m_changed.connect(change_friend_position, sender=Pages.friends.through)


class Membership(models.Model):
    user = models.ForeignKey(UserProfile)
    page = models.ForeignKey(Pages)
    type = models.CharField(max_length=2, choices=MEMBERSHIP_TYPE)
    from_date = models.DateField()
    to_date = models.DateField(null=True,blank=True)
    is_confirmed = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)

    def get_begin_date(self):
        return self.from_date

    def get_end_date(self):
        if self.is_present:
            return 'Present'
        else:
            return self.to_date

    def get_type(self):
        mtype = [mtype for mtype in MEMBERSHIP_TYPE if mtype[0] == self.type]
        return mtype[0][1]

    def get_name(self):
        return self.user.get_full_name()

    def get_user(self):
        return self.user

    def old(self):
        self.is_new = False
        self.save()

    def confirm(self):
        self.is_confirmed = True
        self.save()

    def decline(self):
        self.get_user().set_option('pages_removed__%s__%s' % (self.page.id, self.type), datetime.today().strftime('%m/%d/%Y'))
        self.delete()


class Topics(models.Model):
    name = models.CharField(max_length=2000)
    user = models.ForeignKey(UserProfile)
    page = models.ForeignKey(Pages)
    privacy = models.CharField(max_length=1, choices=TOPIC_PRIVACY_SET, default='P')
    members = models.CharField(max_length=20, choices=TOPIC_MEMBERS_SET, default='A')
    tagged = models.ManyToManyField(Pages, related_name="tagged_in_topics", null=True, blank=True)
    content = models.TextField(blank=True)
    viewed = models.ManyToManyField(UserProfile, related_name="viewed_topics", null=True, blank=True)
    following = models.ManyToManyField(UserProfile, related_name="following_topics", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def get_privacy(self):
        privacy = self.privacy
        for pr in TOPIC_PRIVACY_SET:
            if privacy in pr:
                return pr[1]

    def get_feed(self):
        feed = self.posts.all()
        return feed

    def get_views_count(self):
        viewed = self.viewed.count()
        return viewed

    def get_posts_count(self):
        viewed = self.posts.count()
        return viewed

    def get_comment_count(self):
        count = 0
        # find all posts in topic
        posts = self.posts.all()
        for post in posts:
            comms_count = comments.get_model().objects.filter(
                            content_type=ContentType.objects.get_for_model(post.get_post()),
                            object_pk=post.pk,
                            site__pk=settings.SITE_ID,
                            is_removed=False,
                            ).count()
            count = count + comms_count
        return count

    def get_last_post_date(self):
        posts = self.posts.all()
        if posts:
            post = posts.latest('date')
            return post.date
        else:
            return None

    def get_last_comment_date(self):
        # Im so sorry, db
        now = timezone.now()
        delta = dateclass.timedelta(days=365 * 5)
        latest_date = now - delta
        oldest = latest_date
        # find all posts in topic
        posts = self.posts.all()
        # find latest comment date for each
        if posts:
            for post in posts:
                comms = comments.get_model().objects.filter(
                        content_type=ContentType.objects.get_for_model(post.get_post()),
                        object_pk=post.pk,
                        site__pk=settings.SITE_ID,
                        is_removed=False,
                        )
                if comms:
                    new_date = comms.latest('submit_date')
                    if new_date.submit_date > latest_date:
                        latest_date = new_date.submit_date
        if latest_date != oldest:
            return latest_date
        else:
            return None

