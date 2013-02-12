from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
from celery.contrib import rdb

from django.core import serializers
from django.template.loader import render_to_string

from .redis_connection import r, get_active_users
import json

from account.models import UserProfile
from messaging.models import Messaging
from chat.models import *
from django.db.models.query import Q
from django.core import serializers

import datetime

class ProcessMessage(Task):
    def run(self, user, from_user, num_messages, message='', kind='chat', **kwargs):
        # this task will save chat message
        logger = ProcessMessage.get_logger()
        logger.info('task complete for %s, %s' % (user, message))
        #emit_to_channel()
        #r = redis.StrictRedis(host='localhost', port=6379, db=0)
        try:
            user_obj = UserProfile.objects.get(username = from_user)
            to_user = UserProfile.objects.get(username = user)
        except:
            return False
        # processing new window
        template1 = render_to_string('chat/names.html', {'user':user_obj})
        template2 = render_to_string('chat/messages.html', {'user':user_obj, 'message':message, 'kind':kind })
        template3 = render_to_string('chat/message.html', {'user':user_obj, 'message':message })
        #data = serializers.serialize("json", user_obj)
        # Check if user is online
        if to_user in list(get_active_users()):
            r.publish(user, json.dumps({'names':template1, 'message':template3, 'messages':template2, 'kind':kind , 'username': from_user}))
            online = True
        else:
            online = False
        if message:
            Messaging(user=user_obj, user_to=to_user, content=message, read=online, viewed=online, in_chat=online).save()
        return True
tasks.register(ProcessMessage)


class SaveMessageHistory(Task):
    def run(self, username, usernames, list_opened, **kwargs):
        logger = ProcessMessage.get_logger()
        try:
            user = UserProfile.objects.get(username=username)
        except:
            return False
        user_chat, created = Chat.objects.get_or_create(user=user)
        user_chat.tabs_to.clear()
        if list_opened:
            user_chat.chat_list = True
            user_chat.save()
        else:
            user_chat.chat_list = False
            user_chat.save()
        logger.info(usernames)
        for user_obj in usernames:
            try:
                friend = UserProfile.objects.get(username=user_obj.get('username'))
            except:
                continue
            chat_history, created = ChatHistory.objects.get_or_create(tab_from=user_chat, from_user=friend)
            chat_history.active = user_obj.get('active')
            chat_history.opened = user_obj.get('opened')
            chat_history.save()
        #user_chat.tabs_to = usernames
        #user_chat.save()
        return True
tasks.register(SaveMessageHistory)


class LoadMessageHistory(Task):
    def run(self, username, minutes_ago=5, **kwargs):
        try:
            user = UserProfile.objects.get(username=username)
        except:
            return False
        try:
            user_chat = Chat.objects.get(user=user)
        except:
            return False
        freinds = user_chat.tabs_to.split(',')
        logger = ProcessMessage.get_logger()
        logger.info('freinds %s' % (freinds))
        since = user_chat.date - datetime.timedelta(minutes=minutes_ago)
        logger.info('since %s' % (since))
        for friend in freinds:
            try:
                friend_obj = UserProfile.objects.get(username=friend)
            except:
                continue
            messages = Messaging.objects.filter(Q(user=user_chat.user, user_to=friend_obj) | Q(user=friend_obj, user_to=user_chat.user)) \
            .filer(date__gte=since) \
            .order_by('date')
            logger.info('messages %s' % (messages.count()))
            r.publish(user, serializers.serialize("json", messages))
        return True
tasks.register(LoadMessageHistory)


class PublishActiveUsers(Task):
    def run(self, username, **kwargs):
        logger = PublishActiveUsers.get_logger()
        try:
            user_obj = UserProfile.objects.get(username = username)
            friends = user_obj.get_friends()
        except:
            return False
        active = list(get_active_users())
        active = [u.username for u in active if u in friends]
        logger.info(active)
        r.publish(username, json.dumps({'active':active, 'type':'active'}))
        return True
tasks.register(PublishActiveUsers)

