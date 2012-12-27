# Create your views here.
from django.http import *
from haystack.views import SearchView
from notification.models import Notification
from django.contrib.auth.decorators import login_required
from haystack.query import SearchQuerySet
from account.models import UserProfile
from pages.models import Pages
from django.db.models import Q

try:
    import json
except ImportError:
    import simplejson as json

class CustumSearchView(SearchView):
    def __name__(self):
        return "FacetedSearchView"

    def extra_context(self):
        extra = super(CustumSearchView, self).extra_context()

        extra['not_count'] =  Notification.objects.filter(user=self.request.user, read=False).count()
        #extra['request'] =  self.request

        return extra


@login_required
def auto_complete(request):
    term = request.GET.get('term',None)
    if term:
        friends = request.user.get_friends().filter(Q(username__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))
    else:
        friends = request.user.get_friends()
    dics = []
    for user in friends:
        dic = {'label':user._get_full_name(),'value':user.username,'id':user.id}
        dics.append(dic)
    return HttpResponse(json.dumps(dics), "application/json")


@login_required
def auto_pages(request, slug=None):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    admins = page.get_admins()
    term = request.GET.get('term',None)
    if term:
        friends = request.user.get_friends().filter(Q(username__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))
    else:
        friends = request.user.get_friends()
    dics = []
    for user in friends:
        if user not in admins:
            dic = {'label':user._get_full_name(),'value':user.username,'id':user.id}
            dics.append(dic)
    return HttpResponse(json.dumps(dics), "application/json")


@login_required
def auto_calendar(request, slug=None):
    data = []
    pages = []
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    term = request.GET.get('term',None)
    if term:
        pages =  Pages.objects.filter(name__icontains=term).exclude(id=page.id).all()
    for pg in pages:
        dic = {'label':pg.name,'value':pg.username,'id':pg.id}
        data.append(dic)
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def auto_discussions(request, slug=None):
    data = []
    pages = []
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    term = request.GET.get('term',None)
    if term:
        pages =  page.get_friends().filter(name__icontains=term).exclude(id=page.id).all()
    for pg in pages:
        dic = {'label':pg.name,'value':pg.username,'id':pg.id}
        data.append(dic)
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def auto_fav_pages(request):
    data = []
    pages = []
    term = request.GET.get('term',None)
    if term:
        pages =  request.user.get_loved().filter(name__icontains=term)
    for pg in pages:
        dic = {'label':pg.name,'value':pg.username,'id':pg.id}
        data.append(dic)
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def auto_relation(request):
    term = request.GET.get('term',None)
    if term:
        friends = request.user.get_unrelated_friends().filter(Q(username__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))
    else:
        friends = request.user.get_unrelated_friends()
    dics = []
    for user in friends:
        dic = {'label':user._get_full_name(),'value':user.username,'id':user.id}
        dics.append(dic)
    return HttpResponse(json.dumps(dics), "application/json")
