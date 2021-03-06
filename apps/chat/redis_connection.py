"""
Connection to Redis.
"""
import datetime
import time

import redis
from django.conf import settings

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'ONLINE_THRESHOLD', 6379)
REDIS_DB = getattr(settings, 'ONLINE_THRESHOLD', 0)

r = redis.StrictRedis(REDIS_HOST,
                      REDIS_PORT,
                      REDIS_DB)

TOPIC_ViEWS = 't:%s:v'
TOPIC_TRACKER = 'u:%s:t:%s'
ACTIVE_USERS = 'au'
USER_USERNAME = 'u:%s:un'
USER_LAST_SEEN = 'u:%s:s'
USER_DOING = 'u:%s:d'

def get_online_now(user_id):
    from account.models import UserProfile
    try:
        up = UserProfile.objects.get(id=user_id or [])
    except:
        up = []
    return up

def seen_user(user):
    """
    Stores when Users were last seen and updates
    their last seen time in the active users sorted set.
    """
    last_seen = int(time.mktime(datetime.datetime.now().timetuple()))
    r.zadd(ACTIVE_USERS, last_seen, user.pk)
    r.setnx(USER_USERNAME % user.pk, user.username)
    r.set(USER_LAST_SEEN % user.pk, last_seen)

def get_active_users(minutes_ago=2):
    """
    Yields active Users in the last ``minutes_ago`` minutes, returning
    2-tuples of (user_detail_dict, last_seen_time) in most-to-least recent
    order by time.
    """
    if settings.USER_ONLINE_TIMEOUT:
        minutes_ago = settings.USER_ONLINE_TIMEOUT / 60
    since = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)
    since_time = int(time.mktime(since.timetuple()))
    for user_id, last_seen in reversed(r.zrangebyscore(ACTIVE_USERS, since_time,
                                                       'inf', withscores=True)):
        user = get_online_now(user_id)
        if user:
            if user.is_visible:
                yield (
                    user
                    #{'id': int(user_id), 'username': r.get(USER_USERNAME % user_id)}
                    #datetime.datetime.fromtimestamp(int(last_seen)),
                )

def get_last_seen(user):
    last_seen = r.get(USER_LAST_SEEN % user.pk)
    if last_seen:
        last_seen = datetime.datetime.fromtimestamp(int(last_seen))
    else:
        last_seen = user.date_joined
    return last_seen

