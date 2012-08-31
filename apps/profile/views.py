from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from account.models import UserProfile
from notification.models import Notification
from .forms import *

@login_required
def feed(request):
    return render_to_response(
        'profile/feed.html',
        {
            'not_count': Notification.objects.filter(user=request.user).count()
        },
        RequestContext(request)
    )

@login_required
def timeline(request):
    return render_to_response(
        'profile/timeline.html',
        {
            'not_count': Notification.objects.filter(user=request.user).count()
        },
        RequestContext(request)
    )

@login_required
def profile(request, username=None):
    # TODO: Logic here needs to see what relation the current user is to the profile user
    # and compare this against their privacy settings to see what can be seen.
    form = ImageForm()
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return Http404()
    else:
        profile_user = request.user

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            instance = UserProfile.objects.get(id=request.user.id)
            instance.photo = request.FILES['photo']
            instance.save()
            from django.http import HttpResponseRedirect

            return HttpResponseRedirect(request.path)

    return render_to_response(
        'profile/profile.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user).count(),
            'form' : form
        },
        RequestContext(request)
    )

@login_required
def settings(request):

    return render_to_response(
        'profile/settings.html',
        {
        },
        RequestContext(request)
    )

@login_required
def messages(request):

    return render_to_response(
        'profile/messages.html',
        {
        },
        RequestContext(request)
    )  

