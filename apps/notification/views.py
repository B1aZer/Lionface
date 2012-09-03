from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *
from itertools import chain

@login_required
def notifications(request):
    #import pdb;pdb.set_trace()
    list1 = Notification.objects.filter(user=request.user, type="FR").order_by("-date")
    list2 = Notification.objects.filter(user=request.user).exclude(type="FR").order_by("-date")
    result_list = list(chain(list1, list2))

    return render_to_response(
        'notification/notifications.html',
        {
            'notifications': result_list,
            'not_count': Notification.objects.filter(user=request.user,read=False).count()
        },
        RequestContext(request)
    )
