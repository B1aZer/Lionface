# Create your views here.
from django.views.generic import TemplateView
from django.http import *

from django.contrib.auth.decorators import login_required
from account.decorators import active_required

import json

from socketio import socketio_manage
from .chat_socketio import ChatNamespace

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

