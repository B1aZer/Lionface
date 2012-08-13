from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *

@login_required
def notifications(request):
    return render_to_response(
        'notification/notifications.html',
        {
            'notifications': Notification.objects.filter(user=request.user).order_by("date")
        },
        RequestContext(request)
    )