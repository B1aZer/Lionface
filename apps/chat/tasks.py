from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
from celery.contrib import rdb

from django.core import serializers
from django.template.loader import render_to_string

from .redis_connection import r
import json

from account.models import UserProfile

class ProcessMessage(Task):
    def run(self, user, from_user, num_messages, message='', kind='chat', **kwargs):
        # this task will save chat message
        logger = ProcessMessage.get_logger()
        logger.info('task complete for %s, %s' % (user, message))
        #emit_to_channel()
        #r = redis.StrictRedis(host='localhost', port=6379, db=0)
        try:
            user_obj = UserProfile.objects.get(username = from_user)
        except:
            return False
        # processing new window
        template1 = render_to_string('chat/names.html', {'user':user_obj})
        template2 = render_to_string('chat/messages.html', {'user':user_obj, 'message':message, 'kind':kind })
        template3 = render_to_string('chat/message.html', {'user':user_obj, 'message':message })
        #data = serializers.serialize("json", user_obj)
        r.publish(user, json.dumps({'names':template1, 'message':template3, 'messages':template2, 'kind':kind , 'username': from_user}))
        return True
tasks.register(ProcessMessage)


