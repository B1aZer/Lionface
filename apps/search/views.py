# Create your views here.
from haystack.views import SearchView
from notification.models import Notification


class CustumSearchView(SearchView):
    def __name__(self):
        return "FacetedSearchView"

    def extra_context(self):
        extra = super(CustumSearchView, self).extra_context()

        extra['not_count'] =  Notification.objects.filter(user=self.request.user, read=False).count()

        return extra

