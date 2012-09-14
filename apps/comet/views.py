from django.http import *
from messaging.models import Messages

try:
    import json
except ImportError:
    import simplejson as json


def messages_check(request):
    data = {'status':'ok'}
    new_messages = Messages.objects.filter(user_to = request.user, read=False).count()

    data['mess'] = new_messages

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")
