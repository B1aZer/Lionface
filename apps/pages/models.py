from django.db import models
from account.models import UserProfile
from django.core.validators import validate_slug

PAGE_TYPE = (
        ('BS','Business Page'),
        ('NP','Nonprofit Page'),
)

class Pages(models.Model):
    name = models.CharField(max_length='200')
    loves = models.IntegerField(default=0)
    username = models.CharField(max_length='200', validators=[validate_slug], unique=True)
    user = models.ForeignKey(UserProfile, related_name='pages')
    users_loved = models.ManyToManyField(UserProfile, related_name='pages_loved', null=True, blank=True)
    type = models.CharField(max_length='2', choices=PAGE_TYPE)
    category = models.CharField(max_length=100, default='undefined')
    cover_photo = models.ImageField(upload_to="uploads/images", null=True, blank=True)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def get_lovers(self):
        return self.users_loved.all()

    def get_posts(self):
        return self.posts.all()

    @models.permalink
    def get_absolute_url(self):
        return ('pages.views.page', [str(self.username)])
