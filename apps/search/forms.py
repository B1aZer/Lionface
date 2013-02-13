from haystack.forms import ModelSearchForm
from haystack.forms import SearchForm as SF
from haystack.query import SearchQuerySet, SQ
from current_user.middleware import get_current_user
from tags.models import Tag
from pages.models import Pages
from account.models import UserProfile

class SearchForm(ModelSearchForm):

    def search(self):
        def sorting_by_degree(result):
            if result.model is Pages:
                return '--'
            try:
                if result.object.in_followers(user):
                    return 1
                v = result.object.get_degree_for(user)
            except:
                # this could happen
                # run rebuild_index
                v = '--'
            return v
        #res = super(SearchForm, self).search()
        #res = SearchQuerySet().filter(username_auto=self.cleaned_data['q'])
        if len(self.cleaned_data['q'].strip().split(" ")) > 1:
            # if query has 2 and more words in it
            # we can't use EdgeNgrams
            res = SearchQuerySet().filter(content__contains=self.cleaned_data['q'])
        else:
            res = SearchQuerySet().filter(SQ(username_auto=self.cleaned_data['q']) | SQ(email=self.cleaned_data['q']) | SQ(full_name_auto=self.cleaned_data['q']))
        # ajax filter
        filter_val = self.data.get('filter')
        # filtering
        if filter_val == 'businesses':
            res = res.filter(page_type='BS')
        if filter_val == 'nonprofits':
            res = res.filter(page_type='NP')
        if filter_val == 'people':
            res = res.models(UserProfile)
        else:
            res = res.models(UserProfile, Pages)
        if 'account.userprofile' in self.cleaned_data['models']:
            user = get_current_user()
            for one_user in res:
                #if hasattr(one_user.object, 'userprofile'):
                if one_user.object and not isinstance(one_user.object,Tag) and not isinstance(one_user.object,Pages):
                    #if user was not deleted
                    if not one_user.object.check_visiblity("search",user):
                        res = res.exclude(username=one_user.username)
                    # if in blocked list -> exclude
                    if one_user.object in user.get_blocked():
                        res = res.exclude(username=one_user.username)
                    # Ensure the current user isn't in the results.
                    if user != None and one_user.object == user and not isinstance(one_user.object,Pages):
                        res = res.exclude(username=user.username)
            # custom ordering (by DoS)
            #res = sorted(res,key = lambda s : s.object.get_degree_for(user))
            if filter_val in ('businesses','nonprofits'):
                res = sorted(res,key = lambda s: s.object.loves, reverse=True)
            else:
                res = sorted(res,key = sorting_by_degree)
        return res


class TagSearchForm(SF):

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(TagSearchForm, self).search()
        # Remove tags from friendly table
        """
        if sqs.count() > 1:
            for sq in sqs:
                if hasattr(sq.object,'user_tag'):
                    sqs = sqs.exclude(id = sq.id)
        """
        return sqs

