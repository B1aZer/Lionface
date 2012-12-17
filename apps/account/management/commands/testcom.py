from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        from ecomm.models import Bids, Summary
        from django.conf import settings
        from pages.models import PageRequest
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        winnc = Bids.objects.filter(status=3).count()
        max_three = Bids.objects.filter(status=1).order_by('-amount')[:3]
        if max_three.count():
            for bid in max_three:
                stripe_id = bid.get_stripe_id()
                amount = bid.amount * 100
                try:
                    stripe.Charge.create(
                        amount=amount, # 1500 - $15.00 this time
                        currency="usd",
                        customer=stripe_id,
                        description="Charge for %s, user: %s" % (bid.page.name, bid.user)
                    )
                    Summary.objects.create(user=bid.user, page=bid.page, amount=bid.amount, type='B') 
                    self.stdout.write('Charging: %s' % stripe_id)
                    if winnc < 3:
                        bid.status = 3
                        bid.save()
                        pr = PageRequest(from_page = bid.page, to_page = bid.page, type = 'BN')
                        pr.save()
                except:
                    pr = PageRequest(from_page = bid.page, to_page = bid.page, type = 'BE')
                    pr.save()
                    bid.status = 2
                    bid.save()
