import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace


from tasks import ProcessMessage, SaveMessageHistory, PublishActiveUsers, ToggleSound
#from .utils import redis_connection
from django.conf import settings

from django.template.loader import render_to_string

import json

from .redis_connection import r as redis

@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")
        self.nicknames = []
        self.me = []

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
                    #self.log(i.get('data',''))
                    #self.send({'message': i}, json=True)
                    self.emit('chat', json.loads(i.get('data','')))

    def on_join(self, username, name):
        if not username in self.me:
            self.me.append(username)
            self.log("Join/spawn %s" % username)
            self.broadcast_event_not_me('add', username, name)
            self.spawn(self.listener, username)
            #self.join(room)
            self.emit('joined', True)

    def on_refresh_list(self, username):
        PublishActiveUsers.delay(username)

    def on_unjoin(self, username):
        self.log("disconnected from %s" % username)
        red = redis
        red = red.pubsub()
        red.unsubscribe(username)
        self.broadcast_event_not_me('remove', username)
        if username in self.me:
            self.me.remove(username)
        self.disconnect()

    def on_start_chat(self, username, from_user):
        if username not in self.nicknames:
            self.nicknames.append(username)
            ProcessMessage.delay(from_user , username, len(self.nicknames), kind='start' )
        else:
            # no more chat for you
            pass

    def on_user_message(self, username, from_user, msg):
        self.log('{0} message: {1}'.format(username, msg))
        ProcessMessage.delay(username, from_user, len(self.nicknames), msg, 'chat')
        # run celery task
        #self.log('ready %s' % result.get(timeout=20))
        #self.emit_to_room(self.room, 'msg_to_room',
        #    self.socket.session['nickname'], msg)

    def on_user_reply(self, username, from_user, msg):
        self.log('{0} message: {1}'.format(username, msg))
        ProcessMessage.delay(username, from_user, len(self.nicknames), msg, 'reply')

    def on_close_chat(self, username, from_user):
        if username in self.nicknames:
            self.nicknames.remove(username)

    def on_load_history(self, username):
        if username not in self.nicknames:
            self.nicknames.append(username)

    def on_save_history(self, username, usernames, list_opened):
        self.log('saving')
        self.log(username)
        usernames = json.loads(usernames)
        self.log(list_opened)
        SaveMessageHistory.delay(username, usernames, list_opened)

    def on_sound(self, username, value):
        ToggleSound.delay(username, value)
