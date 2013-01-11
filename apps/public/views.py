from django.http import *
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from account.forms import *
from account.models import UserProfile
from tags.models import Tag

from django.db.models import Count
from django.utils import timezone
import datetime as dateclass


try:
    import json
except ImportError:
    import simplejson as json


def home(request):
    return render_to_response(
        'public/home.html',
        {
            'login_form': LoginForm(prefix='login'),
            'signup_form': SignupForm(prefix='signup')
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
    #tags
    now = timezone.now()
    week_ago = now - dateclass.timedelta(7)
    popular_tags = Tag.objects.filter(post__date__gte=week_ago).annotate(num_posts=Count('post')).order_by('-num_posts')[:8]
    #users
    most_followed = UserProfile.objects.annotate(num_followers=Count('followers')).filter(num_followers__gt=0).filter(from_people__status=1).order_by('-num_followers')[:4]

    return render_to_response(
        'public/about.html',
        {
            'popular_tags' : popular_tags,
            'most_followed' : most_followed,
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
    data = {'status': 'OK'}
    name = request.GET.get('name')
    micro = { 'users_total': UserProfile.objects.count() }
    #import pdb;pdb.set_trace()
    if name == 'followers':
        micro['most_followed'] = UserProfile.objects.annotate(num_followers=Count('followers')).filter(num_followers__gt=0).order_by('-num_followers')[:8]
    if name == 'tags':
        now = timezone.now()
        week_ago = now - dateclass.timedelta(7)
        micro['popular_tags'] = Tag.objects.filter(post__date__gte=week_ago).annotate(num_posts=Count('post')).order_by('-num_posts')[:8]
    try:
        data['html'] = render_to_string('public/micro/%s.html' % name, micro
                                        , context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        data['html'] = "Sorry! Wrong template."
    except:
        data = {'status': 'FAIL'}
    return HttpResponse(json.dumps(data), "application/json")


def page404(request):
    return render_to_response(
        '404.html',
        {
        },
        RequestContext(request)
    )


def page500(request):
    return render_to_response(
        '500.html',
        {
        },
        RequestContext(request)
    )
