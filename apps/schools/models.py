from django.db import models
from account.models import UserProfile


class School(models.Model):
    name = models.CharField(max_length=500)
    website = models.URLField()
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=500)
    country = models.CharField(max_length=500)

    approved = models.BooleanField(default=False)

    user_proposed = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
