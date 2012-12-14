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
                    logger.info('Charging: %s' % stripe_id)
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
tasks.register(ProcessBids)

class ReprocessBids(Task):
    def run(self, **kwargs):
        from ecomm.models import Bids
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
                logger.info('ReCharging: %s' % stripe_id)
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
tasks.register(ReprocessBids)

class UpdatePagesFromBids(Task):
    def run(self, **kwargs):
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
tasks.register(UpdatePagesFromBids)


