from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from account.models import UserProfile
from notification.models import Notification
from .forms import *
from django.contrib.auth.forms import PasswordChangeForm

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def feed(request):
    return render_to_response(
        'profile/feed.html',
        {
            'not_count': Notification.objects.filter(user=request.user,read=False).count()
        },
        RequestContext(request)
    )

@login_required
def timeline(request):
    return render_to_response(
        'profile/timeline.html',
        {
            'not_count': Notification.objects.filter(user=request.user,read=False).count()
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
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
            'form' : form
        },
        RequestContext(request)
    )

@login_required
def settings(request):
    changed = False
    if request.method == 'POST':
        if 'change_pass' in request.POST:
            form_pass = PasswordChangeForm(user=request.user, data=request.POST)
            form = UserInfoForm(instance=request.user)
            if form_pass.is_valid():
                form_pass.save()
                changed = True
        elif 'save' in request.POST:
            form = UserInfoForm(request.POST , instance=request.user)
            form_pass = PasswordChangeForm(user=request.user)
            if form.is_valid():
                form.save()
    else:

        form = UserInfoForm(instance=request.user)
        form_pass = PasswordChangeForm(user=request.user)

    return render_to_response(
        'profile/settings.html',
        {
            'form':form,
            'form_pass':form_pass,
            'changed' : changed,
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

@login_required
def filter_add(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'filter_name' in request.POST:
        filter_name = request.POST['filter_name']
        filters = request.user.filters.split(',')
        if filter_name == 'People':
                if 'F' not in filters:
                    filters.append('F')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Pages':
                if 'P' not in filters:
                    filters.append('P')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def filter_remove(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'filter_name' in request.POST:
        filter_name = request.POST['filter_name']
        filters = request.user.filters.split(',')
        if filter_name == 'People':
                if 'F' in filters:
                    filters.remove('F')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Pages':
                if 'P' in filters:
                    filters.remove('P')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
    return HttpResponse(json.dumps(data), "application/json")

