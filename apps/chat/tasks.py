from celery.task import Task
from celery.registry import tasks
from celery.utils.log import get_task_logger
from celery.contrib import rdb

from .redis_connection import r
import json

class ProcessMessage(Task):
    def run(self, user, message, **kwargs):
        # this task will save chat message
        logger = ProcessMessage.get_logger()
        logger.info('task complete for %s, %s' % (user, message))
        #emit_to_channel()
        #r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.publish(user, json.dumps({'name': user, 'message': message}))
        return True
tasks.register(ProcessMessage)


