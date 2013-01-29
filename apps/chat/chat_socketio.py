import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace

from .tasks import ProcessMessage
#from .utils import redis_connection
from django.conf import settings

import json

from .redis_connection import r as redis

@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def listener(self, username):
        # ``redis_connection()`` is an utility function that returns a redis connection from a pool
        #r = redis_connection().pubsub()
        #r.subscribe('socketio')
        red = redis
        red = red.pubsub()
        red.subscribe(username)
        self.log("Subscribed to %s" % username)

        while True:
            for i in red.listen():
                if i['type'] == 'message':
                    self.log('sending')
                    self.log(i.get('data',''))
                    #self.send({'message': i}, json=True)
                    self.emit('chat', json.loads(i.get('data','')))

    def on_join(self, username):
        self.log("Join/spawn")
        self.spawn(self.listener, username)
        #self.join(room)
        return True

    def on_user_message(self, username, msg):
        self.log('{0} message: {1}'.format(username, msg))
        # run celery task
        ProcessMessage.delay(username, msg)
        #self.log('ready %s' % result.get(timeout=20))
        #self.emit_to_room(self.room, 'msg_to_room',
        #    self.socket.session['nickname'], msg)
        return True
