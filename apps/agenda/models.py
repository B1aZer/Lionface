from django.db import models
from pages.models import Pages

class Events(models.Model):
    page = models.ForeignKey(Pages)
    name = models.CharField(max_length='200')
    date = models.DateTimeField()
    date_end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
