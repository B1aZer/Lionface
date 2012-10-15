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
    return render_to_response(
        'public/terms.html',
        {
        },
        RequestContext(request)
    )

def privacy(request):
    return HttpResponse('Ok')

def about(request):
    return render_to_response(
        'public/about.html',
        {
        },
        RequestContext(request)
    )

def feedback(request):
    return render_to_response(
        'public/feedback.html',
        {
        },
        RequestContext(request)
    )
