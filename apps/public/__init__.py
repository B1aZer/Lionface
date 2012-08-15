from django.contrib.sites import models as sites_models
from django.db.models import signals
from django.conf import settings

def create_site(app, created_models, verbosity, **kwargs):
    """
    Create the default site when when we install the sites framework
    """
    if sites_models.Site in created_models:
        sites_models.Site.objects.all().delete()

        site = sites_models.Site()
        site.pk = getattr(settings, 'SITE_ID', 1)
        site.name = getattr(settings, 'SITE_NAME', 'Lionface')
        site.domain = getattr(settings, 'SITE_DOMAIN', 'lionface.org')
        site.save()

signals.post_syncdb.connect(create_site, sender=sites_models)
