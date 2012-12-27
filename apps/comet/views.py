from django.http import *

from messaging.models import Messaging
from account.models import UserProfile
from notification.models import Notification
from post.models import NewsItem

from django.contrib.auth.decorators import login_required

import dateutil.parser

from itertools import chain

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

@login_required
def feed_posts(request):
    data = {'status':'OK'}
    try:
        date = request.GET['date']
    except:
        raise Http404

    filter = request.GET.get('filter', 'None')
    items = []

    date = dateutil.parser.parse(date)
    # to UTC
    date = date.astimezone(dateutil.tz.tzutc())

    initial = request.GET.get('initial', None)
    if initial:
        request.session['feed_date'] = date

    date = request.session.get('feed_date', date)

    if filter in ('B'):
        business_pages = NewsItem.objects.get_business_feed(request.user, date)
        items = list(chain(items, business_pages))
        items = list(set(items))
        items = sorted(items, key=lambda post: post.timestamp, reverse=True)
        data['count'] = len(items)
    elif filter in ('N'):
        nonprofit_pages = NewsItem.objects.get_nonprofit_feed(request.user, date)
        items = list(chain(items, nonprofit_pages))
        items = list(set(items))
        items = sorted(items, key=lambda post: post.timestamp, reverse=True)
        data['count'] = len(items)
    elif filter in ('F','W'):
        items = request.user.get_messages(filter) \
            .remove_page_posts() \
            .remove_similar() \
            .remove_to_other() \
            .filter_blocked(user=request.user) \
            .get_public_posts(request.user) \
            .get_newer_than(date)
        data['count'] = items.count()

    return HttpResponse(json.dumps(data), "application/json")
