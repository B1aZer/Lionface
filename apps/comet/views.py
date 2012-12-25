from django.http import *
from messaging.models import Messaging
from account.models import UserProfile
from notification.models import Notification
from django.contrib.auth.decorators import login_required

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def messages_check(request):
    data = {'status':'ok'}
    new_messages = request.user.new_messages()

    data['mess'] = new_messages

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")

@login_required
def notifiactions_check(request):
    data = {'status':'ok'}
    new_notifiactions = request.user.new_notifcations()

    data['notfs'] = new_notifiactions

    if request.method == 'GET':
            return HttpResponse(json.dumps(data), "application/json")

@login_required
def permissions_check(request):
    data = {'status':'OK'}
    option = request.GET.get('option',None);
    data['option'] = option;
    data['value'] = request.user.check_option(option);
    return HttpResponse(json.dumps(data), "application/json")
