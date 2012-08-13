from django.shortcuts import redirect

# Wrapper to ensure the user isn't logged in.. and if they are redirect them to the home page.
class public_required(object):
    def __init__(self, func):
        self.func = func
        self.__name__ = 'public_required'
        
    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/')
        return self.func(request, *args, **kwargs)
