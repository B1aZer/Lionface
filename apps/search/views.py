# Create your views here.
from django.http import *
from haystack.views import SearchView
from notification.models import Notification
from django.contrib.auth.decorators import login_required
from haystack.query import SearchQuerySet
from account.models import UserProfile

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

        return extra

@login_required
def auto_complete(request):
    data = [ { 'label': "Choice1", 'value': "value1" }]
    term = request.GET.get('term',None)
    if term:
        friends = request.user.friends.filter(username__icontains=term)
    else:
        friends = request.user.friends.all()
    data = [x.username for x in friends]
    data = sorted(data)
    dics = []
    for user in data:
        dic = {'label':user,'value':user}
        dics.append(dic)
    return HttpResponse(json.dumps(dics), "application/json")

