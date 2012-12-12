from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        from ecomm.models import Bids
        from pages.models import Pages
        from django.utils import timezone
        now = timezone.now()
        # no featured
        Pages.objects.filter(featured=True).update(featured=False)
        # expired disabled
        Pages.objects.filter(is_disabled__lte=now).update(is_disabled=None)
        winners = Bids.objects.filter(status=3)
        for bid in winners:
            bid.page.featured = True
            bid.page.save()
        active_bids = Bids.objects.filter(status__in=(1,2,3))
        for bid in active_bids:
            bid.status = 0
            bid.save()


