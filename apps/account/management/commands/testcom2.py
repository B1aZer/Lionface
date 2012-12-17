from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        from ecomm.models import Bids, Summary
        from pages.models import PageRequest
        from django.conf import settings
        from django.utils import timezone
        import datetime as dateclass
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        winnc = Bids.objects.filter(status=3).count()
        error_bids = Bids.objects.filter(status=2)
        for bid in error_bids:
            stripe_id = bid.get_stripe_id()
            amount = bid.amount * 100
            # remove error notifiers
            prs = PageRequest.objects.filter(to_page = bid.page, type = 'BE')
            for pr in prs:
                pr.delete()
            try:
                stripe.Charge.create(
                    amount=amount, # 1500 - $15.00 this time
                    currency="usd",
                    customer=stripe_id,
                    description="Recharge for %s, user: %s" % (bid.page.name, bid.user)
                )
                Summary.objects.create(user=bid.user, page=bid.page, amount=bid.amount, type='B')
                self.stdout.write('ReCharging: %s' % stripe_id)
                if winnc < 3:
                    bid.status = 3
                    bid.save()
                    pr = PageRequest(from_page = bid.page, to_page = bid.page, type = 'BN')
                    pr.save()
            except:
                pr = PageRequest(from_page = bid.page, to_page = bid.page, type = 'BB')
                pr.save()
                now = timezone.now()
                delta = dateclass.timedelta(days=21)
                #delta = dateclass.timedelta(minutes=5)
                bid.page.is_disabled = now + delta
                bid.page.save()
                bid.status = 0
                bid.save()

