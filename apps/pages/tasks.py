from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
from celery.contrib import rdb
logger = get_task_logger(__name__)

class UpdatePageEvent(Task):
    def run(self, **kwargs):
        from django.utils import timezone
        from pages.models import Pages
        import datetime as dateclass
        import pytz
        from post.models import PagePost
        pages = Pages.objects.filter(post_update=True)
        offset = None
        for page in pages:
            now = timezone.now()
            # utc now ?
            if page.user.timezone:
                utz = pytz.timezone(page.user.timezone)
                unow = now.replace(tzinfo=utz)
                offset = unow.utcoffset()
            delta = dateclass.timedelta(days=1)
            deltamins = dateclass.timedelta(minutes=30)
            afterday = now + delta
            period = afterday + deltamins
            if offset:
                afterday = afterday + offset
            if offset:
                period = period + offset
            events = page.events_set.filter(date__gte=afterday,date__lte=period)
            if events.count() > 0:
                for event in events:
                    content = "There's an event in 24 hours: %s" % event.name
                    if event.description:
                        content = content + "\n  Description: %s" % event.description
                    post = PagePost(user=page.user, content=content, page = page)
                    post.save()
tasks.register(UpdatePageEvent)

class DeletePage(Task):
    def run(self, **kwargs):
        from django.utils import timezone
        from pages.models import Pages
        now = timezone.now()
        pages = Pages.objects.all().filter(for_deletion__lte=now)
        if pages.count():
            for page in pages:
                page.delete()
tasks.register(DeletePage)

class ProcessBids(Task):
    def run(self, **kwargs):
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
                    logger.info('Charging: %s' % stripe_id)
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
tasks.register(ProcessBids)

class ReprocessBids(Task):
    def run(self, **kwargs):
        from ecomm.models import Bids
        from django.conf import settings
        import stripe
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
                logger.info('ReCharging: %s' % stripe_id)
                bid.status = 3
                bid.save()
            except:
                # send message
                # block
                bid.status = 2
                bid.save()
tasks.register(ReprocessBids)

class UpdatePagesFromBids(Task):
    def run(self, **kwargs):
        from ecomm.models import Bids
        from pages.models import Pages
        Pages.objects.filter(featured=True).update(featured=False)
        winners = Bids.objects.filter(status=3)
        for bid in winners:
            bid.page.featured = True
            bid.page.save()
        active_bids = Bids.objects.filter(status__in=(1,2,3))
        for bid in active_bids:
            bid.status = 0
            bid.save()
tasks.register(UpdatePagesFromBids)


