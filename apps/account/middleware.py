from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from chat import redis_connection as redis



class TimezoneMiddleware(object):
    def process_request(self, request):
        tz = request.session.get('django_timezone')
        if tz:
            timezone.activate(tz)

class ActiveUserMiddleware:
    def process_request(self, request):
        current_user = request.user
        if request.user.is_authenticated():
            #now = timezone.now()
            redis.seen_user(current_user)
            #cache.set('seen_%s' % (current_user.username), now,
                           #settings.USER_LASTSEEN_TIMEOUT)

