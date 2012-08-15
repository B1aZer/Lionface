from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from account.models import UserProfile

@login_required
def feed(request):
    return render_to_response(
        'profile/feed.html',
        {
        },
        RequestContext(request)
    )

@login_required
def profile(request, username=None):
    # TODO: Logic here needs to see what relation the current user is to the profile user
    # and compare this against their privacy settings to see what can be seen.
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return Http404()
    else:
        profile_user = request.user
        
    return render_to_response(
        'profile/profile.html',
        {
            'profile_user': profile_user
        },
        RequestContext(request)
    )
