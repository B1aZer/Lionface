from django.db import models

# Create your models here.

class Tag(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

