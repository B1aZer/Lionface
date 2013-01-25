import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace

from .tasks import ProcessMessage
from .utils import redis_connection
from django.conf import settings

import redis
import json

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def listener(self, room):
        # ``redis_connection()`` is an utility function that returns a redis connection from a pool
        #r = redis_connection().pubsub()
        #r.subscribe('socketio')
        red = redis.StrictRedis(host='localhost', port=6379, db=0)
        red = red.pubsub()
        red.subscribe('socketio')
        self.log("Subscribed to socketio_io")

        while True:
            for i in red.listen():
                self.log("Sending message")
                self.send({'message': i}, json=True)

    def on_join(self, room):
        self.room = room
        self.log("Join/spawn")
        self.spawn(self.listener, room)
        #self.join(room)
        return True

    def on_nickname(self, nickname):
        self.log('Nickname: {0}'.format(nickname))
        self.nicknames.append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        #nickname = self.socket.session['nickname']
        #self.nicknames.remove(nickname)
        #self.broadcast_event('announcement', '%s has disconnected' % nickname)
        #self.broadcast_event('nicknames', self.nicknames)
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        # run celery task
        ProcessMessage.delay()
        #self.log('ready %s' % result.get(timeout=20))
        #self.emit_to_room(self.room, 'msg_to_room',
        #    self.socket.session['nickname'], msg)
        return True
