from django.http import Http404
from django.utils.decorators import available_attrs

from account.models import UserProfile

from functools import wraps

def unblocked_users(func):
    """ Restrict access for blocked users"""
    @wraps(func, assigned=available_attrs(func))
    def decorator(request, *args, **kwargs):
        if request.user.get_blocked():
            username = kwargs.get('username',None)
            if username != None:
                try:
                    profile_user = UserProfile.objects.get(username=username)
                except UserProfile.DoesNotExist:
                    #this will raise http404 later anyway
                    return func(request, *args, **kwargs)
            else:
                return func(request, *args, **kwargs)
            if profile_user in request.user.get_blocked() and profile_user != request.user:
                raise Http404
            else:
                return func(request, *args, **kwargs)
        else:
            return func(request, *args, **kwargs)
    return decorator

