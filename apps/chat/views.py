# Create your views here.
from django.views.generic import TemplateView
from django.http import *

from django.contrib.auth.decorators import login_required
from account.decorators import active_required

from messaging.models import Messaging
from chat.models import *
from django.db.models.query import Q
from django.core import serializers

import json

from socketio import socketio_manage
from .chat_socketio import ChatNamespace

from django.template.loader import render_to_string

class HomeView(TemplateView):
    template_name = 'chat/chat.html'


@active_required
@login_required
def change_status(request):
    data = {'status': 'FAIL'}
    status = request.POST.get('status')
    if not status:
        raise Http404
    if status == 'online':
        request.user.is_visible = True
    else:
        request.user.is_visible = False
    try:
        request.user.save()
        data['status'] = 'OK'
    except:
        pass
    return HttpResponse(json.dumps(data), "application/json")


def load_history(request):
    data = {'status':'FAIL'}
    user = request.user
    minutes_ago = 5
    try:
        user_chat = Chat.objects.get(user=user)
    except:
        return False
    friends = user_chat.tabs_to.replace('[','') \
                                .replace(']','') \
                                .replace('u\'','') \
                                .replace('\'','') \
                                .replace('"','') \
                                .split(',')
    since = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)
    for friend in friends:
        try:
            friend_obj = UserProfile.objects.get(username=friend.strip())
        except:
            continue
        messages = Messaging.objects.filter(Q(user=user_chat.user, user_to=friend_obj) | Q(user=friend_obj, user_to=user_chat.user)) \
        .filter(in_chat=True).filter(date__gte=since) \
        .order_by('date')
        #data[friend.strip()] = serializers.serialize("json", messages)
        names_templ = render_to_string('chat/names.html', {'user':friend_obj})
        mess_templ = render_to_string('chat/history_messages.html', {'user':friend_obj, 'messages':messages})
        data[friend.strip()] = {'names': names_templ, 'messages' : mess_templ}
        data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")
