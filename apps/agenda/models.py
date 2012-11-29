from django.db import models
from pages.models import Pages

class Events(models.Model):
    page = models.ForeignKey(Pages)
    name = models.CharField(max_length='200')
    date = models.DateTimeField()
    date_end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __repr__(self):
        return '<Event %s> %s' % (self.id, self.name)

    def get_locations(self):
        locs = self.locations_set.all()
        return locs

    def get_locations_list(self):
        locs = [{
                'lat':loc.lat,
                'lng':loc.lng
                } for loc in self.locations_set.all()]
        return locs

class Locations(models.Model):
    event = models.ForeignKey(Events)
    location = models.CharField(max_length='2000', blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
