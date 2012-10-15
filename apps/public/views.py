from django.http import *
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from account.forms import *
from account.models import UserProfile

try:
    import json
except ImportError:
    import simplejson as json

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

def micro(request):
    data = {'status':'OK'}
    name = request.GET.get('name')
    try:
        data['html'] = render_to_string('public/micro/%s.html' % name,
                {
                    'users_total' : UserProfile.objects.count(),
                }, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        data['html'] = "Sorry! Wrong template."
    except:
        data = {'status':'FAIL'}
    return HttpResponse(json.dumps(data), "application/json")
