from django.db import models
from account.models import *

# Create your models here.

class Tag(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def get_posts(self):
        return self.post_set.all()

    def get_posts_count(self):
        return self.post_set.count()

class User_Tag(Tag):
    user = models.ForeignKey(UserProfile)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'user_tag'
        verbose_name_plural = 'user_tags' 


