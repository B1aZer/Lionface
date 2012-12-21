from django.db import models
from pages.models import Pages

PRIVACY_SET = (
    ('P','Public'),
    ('A','Admins'),
    ('E','Employees'),
    ('I','Interns'),
    ('V','Volunteers'),
)


class Events(models.Model):
    page = models.ForeignKey(Pages)
    tagged = models.ManyToManyField(Pages, related_name="tagged_in", null=True, blank=True)
    name = models.CharField(max_length='200')
    date = models.DateTimeField()
    date_end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=20, choices=PRIVACY_SET, default='P')
    allow_commenting = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)

    def __repr__(self):
        return '<Event %s> %s' % (self.id, self.name)

    def get_locations(self):
        locs = self.locations_set.all()
        return locs

    def remove_locations(self):
        self.get_locations().delete()
        return True

    def get_locations_list(self):
        locs = [{
                'lat':loc.lat,
                'lng':loc.lng
                } for loc in self.locations_set.all()]
        return locs

    def get_privacy(self):
        return self.privacy.split(',')

    def get_tagged_pages(self, page=None):
        tagged = []
        if self.tagged.count() > 1:
            if page:
                tagged = [pg for pg in self.tagged.all() if pg != page]
            else:
                tagged = [pg for pg in self.tagged.all() if pg != self.page]
        return tagged

    def get_owner(self):
        return self.page.user

    def save(self, *args, **kwargs):
        """ Adding page to tagged """
        super(Events, self).save(*args, **kwargs)
        self.tagged.add(self.page)


class Locations(models.Model):
    event = models.ForeignKey(Events)
    location = models.CharField(max_length='2000', blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
