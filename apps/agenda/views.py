from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    return render_to_response(
            'calendar/calendar.html',
            {
            },
            RequestContext(request)
        )
