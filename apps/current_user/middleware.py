'''
Created on 25 May 2009

@author: dalore
'''

from django.db.models import signals
from django.utils.functional import curry
from django.utils.decorators import decorator_from_middleware

from current_user import registration

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_current_user_id():
    cuser = get_current_user()
    if cuser:
        return cuser.id
    else:
        return None

def set_current_user(user):
    """
    for debugging purposes
    """
    setattr(_thread_locals, 'user', user)


def update_users(sender, instance, **kwargs):
    # if instance is not created, return
    #if instance.pk is not None:
    #    return
    registry = registration.FieldRegistry()
    if sender in registry:
        for field in registry.get_fields(sender):
            if instance.pk is None or field.editable:
                setattr(instance, field.name, get_current_user())

signals.pre_save.connect(update_users, weak=False)

class CurrentUserMiddleware(object):
    def process_request(self, request):
        if not '/socket.io/' in request.path:
            if hasattr(request, 'user') and request.user.is_authenticated():
                from account.models import UserProfile
                request.user = UserProfile.objects.get(user_ptr=request.user)
                user = request.user
            else:
                user = None
            _thread_locals.user = user
    
               
    
record_current_user = decorator_from_middleware(CurrentUserMiddleware)
