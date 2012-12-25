from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from models import *
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
    import json
except ImportError:
    import simplejson as json


@login_required
def notifications(request, username=None):
    #import pdb;pdb.set_trace()
    list1 = Notification.objects.filter(user=request.user, type="FR").exclude(hidden=True).order_by("-date")
    list2 = Notification.objects.filter(user=request.user).exclude(type__in=("FR","FA","FF","FM")).exclude(hidden=True).order_by("-date")
    list3 = Notification.objects.filter(user=request.user, type__in=("FA","FF","FM")).exclude(hidden=True).order_by("-date")
    #result_list = list(chain(list1, list2, list3))
    result_list = list2

    #remove deleted content posts:
    """
    for item in result_list:
        if item.type == "PP":
            news_item_in = item.content_object.newsitem_set.all()
            if not news_item_in:
                result_list.remove(item)
    """

    paginator = Paginator(result_list, 7)
    result_list = paginator.page(1)

    if request.method == 'GET':
        page = request.GET.get('page', None)
        if page:
            try:
                result_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                result_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                result_list = paginator.page(paginator.num_pages)

            data = render_to_string('notification/left.html', {
                'notifications': result_list,
            }, context_instance=RequestContext(request))
            return HttpResponse(json.dumps(data), "application/json")

    return render_to_response('notification/notifications.html', {
        'notifications': result_list,
        'notification_requests': list1,
        'notifications_friends': list3,
        'not_count': Notification.objects \
            .filter(user=request.user,read=False) \
            .count(),
    },  RequestContext(request))


def hide_notification(request, notf_id, username=None):
    data = {'status':'FAIL'}
    try:
        notf = Notification.objects.get(id=notf_id)
    except:
        raise Http404
    notf.delete()
    data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")
