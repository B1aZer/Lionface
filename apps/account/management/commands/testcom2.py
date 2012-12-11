from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        from ecomm.models import Bids
        from django.conf import settings
        import stripe
        import pdb;pdb.set_trace()
        stripe.api_key = settings.STRIPE_API_KEY
        error_bids = Bids.objects.filter(status=2)
        for bid in error_bids:
            stripe_id = bid.user.get_stripe_id()
            amount = bid.amount * 100
            try:
                stripe.Charge.create(
                    amount=amount, # 1500 - $15.00 this time
                    currency="usd",
                    customer=stripe_id
                )
                self.stdout.write('ReCharging: %s' % stripe_id)
                bid.status = 3
                bid.save()
            except:
                # send message
                # block
                bid.status = 2
                bid.save()


