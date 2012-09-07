from haystack.forms import ModelSearchForm
from current_user.middleware import get_current_user

class SearchForm(ModelSearchForm):
    def search(self):
        res = super(SearchForm, self).search()
        if 'auth.user' in self.cleaned_data['models']:
            # Ensure the current user isn't in the results.
            user = get_current_user()
            if user != None:
                res = res.exclude(username=user.username)
            # TODO: Privacy settings will come in here too at some point.
        return res

