from haystack.forms import ModelSearchForm
from haystack.forms import SearchForm as SF
from haystack.query import SearchQuerySet, SQ
from current_user.middleware import get_current_user

class SearchForm(ModelSearchForm):

    def search(self):
        #res = super(SearchForm, self).search()
        #res = SearchQuerySet().filter(username_auto=self.cleaned_data['q'])
        res = SearchQuerySet().filter(SQ(username_auto=self.cleaned_data['q']) | SQ(email=self.cleaned_data['q']) | SQ(first_auto=self.cleaned_data['q']) | SQ(last_auto=self.cleaned_data['q']))
        if 'account.userprofile' in self.cleaned_data['models']:
            # Ensure the current user isn't in the results.
            user = get_current_user()
            if user != None:
                res = res.exclude(username=user.username)
            # TODO: Privacy settings will come in here too at some point.
            for one_user in res:
                #if hasattr(one_user.object, 'userprofile'):
                if one_user.object:
                    #if user was not deleted
                    if not one_user.object.check_visiblity("search",user):
                        res = res.exclude(username=one_user.username)
                    # if in blocked list -> exclude
                    if one_user.object in user.get_blocked():
                        res = res.exclude(username=one_user.username)
                else:
                    res = res.exclude(username=one_user.username)
        return res


class TagSearchForm(SF):

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(TagSearchForm, self).search()
        # Remove tags from friendly table
        if sqs.count() > 1:
            for sq in sqs:
                if hasattr(sq.object,'user_tag'):
                    sqs = sqs.exclude(id = sq.id)
        return sqs


