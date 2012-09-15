from django.db import models

# Create your models here.

class Smiley(models.Model):
    pattern = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='smileys')

    def __unicode__(self):
        return self.description or self.pattern
