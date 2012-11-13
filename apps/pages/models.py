from django.db import models
from account.models import UserProfile
from django.core.validators import validate_slug, URLValidator

PAGE_TYPE = (
        ('BS','Business Page'),
        ('NP','Nonprofit Page'),
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

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def get_lovers(self):
        return self.users_loved.all()

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

    def get_friends_count(self):
        return self.friends.count()

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

