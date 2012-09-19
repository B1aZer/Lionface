from django.http import *
from messaging.models import Messaging
from notification.models import Notification

try:
    import json
except ImportError:
    import simplejson as json


def messages_check(request):
    data = {'status':'ok'}
    new_messages = Messaging.objects.filter(user_to = request.user, read=False).count()

    data['mess'] = new_messages

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")

def notifiactions_check(request):
    data = {'status':'ok'}
    new_notifiactions = Notification.objects.filter(user=request.user,read=False).count()

    data['notfs'] = new_notifiactions

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")
