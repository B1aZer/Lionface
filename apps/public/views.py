from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from account.forms import *

def home(request):
    return render_to_response(
        'public/home.html',
        {
            'login_form': LoginForm(prefix='login')
        },
        RequestContext(request)
    )

def terms(request):
    return HttpResponse('Ok')

def privacy(request):
    return HttpResponse('Ok')

def about(request):
    return HttpResponse('Ok')

def feedback(request):
    return HttpResponse('Ok')
