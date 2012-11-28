from django.db import models
from account.models import UserProfile
from django.core.validators import validate_slug, URLValidator
from django.db.models.signals import m2m_changed
from django.db.models import F
from datetime import datetime
import logging
import cPickle

from images.fields import ImageWithThumbField


PAGE_TYPE = (
        ('BS','Business Page'),
        ('NP','Nonprofit Page'),
)

MEMBERSHIP_TYPE = (
        ('VL','Volunteer'),
        ('IN','Intern'),
        ('EM','Employee'),
)

class PageRequest(models.Model):
    from_page = models.ForeignKey('Pages', related_name='from_page')
    to_page = models.ForeignKey('Pages', related_name='to_page')
    date = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("from_page", "to_page")

    def accept(self):
        self.from_page.friends.add(self.to_page)
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


class Pages(models.Model):
    name = models.CharField(max_length='200')
    friends = models.ManyToManyField('self', related_name='friends')
    loves = models.IntegerField(default=0)
    username = models.CharField(max_length='200', validators=[validate_slug], unique=True)
    url = models.URLField(max_length='2000', null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    user = models.ForeignKey(UserProfile, related_name='pages')
    users_loved = models.ManyToManyField(UserProfile, related_name='pages_loved', null=True, blank=True)
    admins = models.ManyToManyField(UserProfile, related_name='pages_admin', null=True, blank=True)
    type = models.CharField(max_length='2', choices=PAGE_TYPE)
    category = models.CharField(max_length=100, default='undefined')
    cover_photo = models.ImageField(upload_to="uploads/images", default='uploads/images/noCoverImage.png')
    photo = ImageWithThumbField(upload_to="uploads/images", default='uploads/images/noProfilePhoto.png')
    has_employees = models.BooleanField(default=True)
    text_employees = models.TextField(blank=True)
    has_interns = models.BooleanField(default=True)
    text_interns = models.TextField(blank=True)
    has_volunteers = models.BooleanField(default=True)
    text_volunteers = models.TextField(blank=True)
    members = models.ManyToManyField(UserProfile, related_name="member_of", through='Membership')
    post_update = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __repr__ (self):
        return '<Page %s> %s' % (self.id, self.username)

    def get_lovers(self):
        return self.users_loved.all()

    def get_lovers_count(self):
        return self.users_loved.count()

    def get_lovers_public(self):
        lovers = self.users_loved.all()
        lovers = [lover for lover in lovers if not lover.check_option('loves','Private')]
        return lovers

    def get_lovers_public_count(self):
        lovers = self.users_loved.all()
        lovers = [lover for lover in lovers if not lover.check_option('loves','Private')]
        return len(lovers)

    def get_lovers_private_count(self):
        lovers = self.users_loved.all()
        lovers = [lover for lover in lovers if lover.check_option('loves','Private')]
        return len(lovers)

    def get_lovers_ordered(self):
        # limit to 7x10 rows
        lovers = self.get_lovers_public()[:70]
        lovers = sorted(lovers, key=lambda s: s.get_followers_count(), reverse=True)
        return lovers

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
        return self.to_page.filter(is_hidden=False, is_accepted=False)

    def get_requests_count(self):
        return self.get_requests().count()

    def get_accepted_requests(self):
        return self.from_page.filter(is_hidden=False, is_accepted=True)

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

    def get_volunteers_ordered(self):
        members = Membership.objects.filter(page=self, type='VL', is_confirmed=True)[:70]
        users = [member.get_user() for member in members if not member.get_user().check_option('vie_pages','Private')]
        users = sorted(users, key=lambda s: s.get_followers_count(), reverse=True)
        return users

    def get_emloyees_ordered_count(self):
        members = Membership.objects.filter(page=self, type='EM', is_confirmed=True).count()
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

    def update_option(self):
        return self.post_update

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
    type = models.CharField(max_length='2', choices=MEMBERSHIP_TYPE)
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



