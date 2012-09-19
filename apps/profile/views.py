from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string

from account.models import UserProfile
from messaging.models import Messaging
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
                mess = Messaging(user=request.user,user_to=user_to,content=content)
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
        users = []

        if 'Friends' in request.GET and profile_user.check_visiblity('friend_list',request.user):
            friends = profile_user.friends.all()
            users.extend(friends)
            data['html'] = [x.username for x in friends]
        if 'Following' in request.GET and profile_user.check_visiblity('following_list',request.user):
            following = profile_user.following.all()
            users.extend(following)
            data['html'] = [x.username for x in following]
        if 'Followers' in request.GET and profile_user.check_visiblity('follower_list',request.user):
            followers = profile_user.followers.all()
            users.extend(followers)
            data['html'] = [x.username for x in followers]

        if len(data) > 0 and 'ajax' in request.GET:
            data['html'] = render_to_string('profile/related_users.html',
                {
                    'current_user' : profile_user,
                    'users' : list(set(users)),
                }, context_instance=RequestContext(request))
            return HttpResponse(json.dumps(data), "application/json")



    return render_to_response(
        'profile/related.html',
        {
            'profile_user' : profile_user,
            'current_user' : profile_user,
            'users' : users,
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

@login_required
def reset_picture(request):
    request.user.photo = 'images/noProfilePhoto.png'
    request.user.save()
    return redirect('profile.views.profile')
