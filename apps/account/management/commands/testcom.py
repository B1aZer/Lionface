from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        from ecomm.models import Bids
        from django.conf import settings
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        max_three = Bids.objects.filter(status=1).order_by('-amount')[:3]
        if max_three.count():
            for bid in max_three:
                stripe_id = bid.user.get_stripe_id()
                amount = bid.amount * 100
                try:
                    stripe.Charge.create(
                        amount=amount, # 1500 - $15.00 this time
                        currency="usd",
                        customer=stripe_id
                    )
                    self.stdout.write('Charging: %s' % stripe_id)
                    bid.status = 3
                    bid.save()
                    #except stripe.CardError, e:
                    # declined card
                    # mark unsuccessful
                    #pass
                except:
                    # send message
                    bid.status = 2
                    bid.save()

