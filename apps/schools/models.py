from django.db import models
from account.models import UserProfile


class Alum(models.Model):
    user = models.ForeignKey(UserProfile)
    year = models.PositiveIntegerField()

    def __unicode__(self):
        return '{0} - {1}'.format(self.user, self.year)

    class Meta:
        verbose_name = 'alum'
        verbose_name_plural = 'alumni'


class School(models.Model):
    name = models.CharField(max_length=500)
    website = models.URLField()
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=500)
    country = models.CharField(max_length=500)

    approved = models.BooleanField(default=False)

    alumni = models.ManyToManyField(Alum, blank=True, null=True)

    user_proposed = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.name

    def people_count(self):
        return self.alumni.all().count()

    class Meta:
        verbose_name = 'school'
        verbose_name_plural = 'schools'
