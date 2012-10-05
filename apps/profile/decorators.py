from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import available_attrs

from functools import wraps

def access_required(permission):
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner_decorator(request, *args, **kwargs):
            if permission == 'admin':
                if request.session['user_profile'].is_account_admin == 1:
                    return func(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse('dashboard'))

        return wraps(func)(inner_decorator)

    return decorator

