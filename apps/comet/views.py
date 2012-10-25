from django.http import *
from messaging.models import Messaging
from notification.models import Notification

try:
    import json
except ImportError:
    import simplejson as json


def messages_check(request):
    data = {'status':'ok'}
    new_messages = Messaging.objects.filter(user_to = request.user, viewed=False).count()

    data['mess'] = new_messages

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")

def notifiactions_check(request):
    data = {'status':'ok'}
    new_notifiactions = request.user.new_notifcations()

    data['notfs'] = new_notifiactions

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")
