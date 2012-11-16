from django.db import models
from account.models import UserProfile
from django.core.validators import validate_slug, URLValidator
from django.db.models.signals import m2m_changed
from django.db.models import F
from datetime import datetime

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


"""
class Membership(models.Model):
    user = models.ForeignKey("UserProfile")
    page = models.ForeignKey("Pages")
    type = models.CharField(max_length='2', choices=MEMBERSHIP_TYPE)
    from_date = models.DateField()
    to_date = models.DateField(default=datetime.now)
    """


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
    has_employees = models.BooleanField(default=True)
    text_employees = models.TextField(blank=True)
    has_interns = models.BooleanField(default=True)
    text_interns = models.TextField(blank=True)
    has_volunteers = models.BooleanField(default=True)
    text_volunteers = models.TextField(blank=True)
    admins = models.ManyToManyField(UserProfile, related_name='pages_admin', null=True, blank=True)
    #members = models.ManyToManyField(UserProfile, related_name="member_of", through='Membership')

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

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

    def get_admins(self):
        return self.admins.all()

    def get_community_admins(self):
        comm_admins = [admin
                for admin in self.admins.all()
                    if admin.check_option('pages_community__%s' % self.id)]
        return comm_admins

    def get_requests(self):
        return self.to_page.filter(is_hidden=False, is_accepted=False)

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

    def check_employees(self):
        return self.has_employees

    def check_interns(self):
        return self.has_interns

    def check_volunteers(self):
        return self.has_volunteers

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


def change_friend_position(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    if action =='post_add':
        try:
            page = model.objects.get(id=pk_set.pop())
        except KeyError:
            # debugging
            return
        friend = instance
        #import pdb;pdb.set_trace()
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
            return
        try:
            page_pos = PagePositions.objects.get(to_page=page, from_page=friend)
            page_pos.delete()
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



