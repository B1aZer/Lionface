from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from account.models import UserProfile
from messaging.models import Messages
from notification.models import Notification
from .forms import *
from messaging.forms import MessageForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

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
    form_mess = MessageForm()

    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return Http404()
    else:
        profile_user = request.user

    if request.method == 'POST':
        if 'image' in request.POST:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                instance = UserProfile.objects.get(id=request.user.id)
                instance.photo = request.FILES['photo']
                instance.save()
                return HttpResponseRedirect(request.path)

        if 'message' in request.POST:
            form_mess = MessageForm(request.POST)
            if form_mess.is_valid():
                user_to = profile_user
                content = form_mess.cleaned_data['content']
                mess = Messages(user=request.user,user_to=user_to,content=content)
                mess.save()
                return HttpResponseRedirect(request.path)

    return render_to_response(
        'profile/profile.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
            'form' : form,
            'form_mess' : form_mess,
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
            for name in request.POST:
                if name.find('option') >= 0:
                    try:
                        option = request.user.useroptions_set.get(name=name)
                        option.value = request.POST[name]
                        option.save()
                    except ObjectDoesNotExist:
                        request.user.useroptions_set.create(name=name,value=request.POST[name])
            if form.is_valid():
                form.save()
    else:

        form = UserInfoForm(instance=request.user,initial = request.user.get_options())
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
def related_users(request,username=None):
    if not username:
        profile_user = request.user
    else:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return Http404()

    if request.method == 'GET':
        data = {}
        if 'friends' in request.GET:
            friends = profile_user.friends.all()
            data['html'] = [x.username for x in friends]
            return HttpResponse(json.dumps(data), "application/json")
        if 'following' in request.GET:
            following = profile_user.following.all()
            data['html'] = [x.username for x in following]
            return HttpResponse(json.dumps(data), "application/json")
        if 'followers' in request.GET:
            followers = profile_user.followers.all()
            data['html'] = [x.username for x in followers]
            return HttpResponse(json.dumps(data), "application/json")

    following = profile_user.following.all()

    return render_to_response(
        'profile/related.html',
        {
            'profile_user' : profile_user,
            'following' : following,
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

