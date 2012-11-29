from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

class UpdatePageEvent(Task):
    def run(self, **kwargs):
        from django.utils import timezone
        from pages.models import Pages
        import datetime as dateclass
        #from datetime import datetime
        from pytz import timezone
        from post.models import PagePost
        pages = Pages.objects.filter(post_update=True)
        now = timezone.now()
        delta = dateclass.timedelta(days=1)
        deltamins = dateclass.timedelta(minutes=30)
        afterday = now + delta
        period = afterday + deltamins
        for page in pages:
            #gte ?
            events = page.events_set.filter(date__gte=afterday,date__lte=period)
            if events.count() > 0:
                for event in events:
                    post = PagePost(user=page.user, content='event soon: %s' % event.name, page = page)
                    post.save()
tasks.register(UpdatePageEvent)
