from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
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
                    post = PagePost(user=page.user, content='event soon: %s' % event.name, page = page)
                    post.save()
tasks.register(UpdatePageEvent)
