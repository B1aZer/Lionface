import settings
from django.contrib.sites.models import Site

def current_site(context):
    return {'current_site': Site.objects.get_current()}