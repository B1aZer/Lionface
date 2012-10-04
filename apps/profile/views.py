from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string

from account.models import UserProfile
from messaging.models import Messaging
from post.models import Albums
from notification.models import Notification
from messaging.forms import MessageForm
from .forms import *

from django.db.models import F

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
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
def profile_image(request, username=None):
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404
    else:
        profile_user = request.user

    return render_to_response(
        'profile/image.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
        },
        RequestContext(request)
    )

@login_required
def profile(request, username=None):
    # TODO: Logic here needs to see what relation the current user is to the profile user
    # and compare this against their privacy settings to see what can be seen.
    form = ImageForm()
    form_mess = MessageForm()
    form_mess.fields['content'].widget.attrs['rows'] = 7

    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404
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


    if request.method == 'GET' and 'albums' in request.GET:
        """Albums view"""
        return render_to_response(
            'profile/albums.html',
            {
                'profile_user': profile_user,
                'not_count': Notification.objects.filter(user=request.user,read=False).count(),
                'form_mess' : form_mess,
                'albums' : request.user.albums_set.all().order_by('position'),
            },
            RequestContext(request)
        )

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
def albums(request):
    """Albums view"""
    profile_user = request.user

    return render_to_response(
        'profile/albums.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
            'albums' : request.user.albums_set.all().order_by('position'),
        },
        RequestContext(request)
    )

@login_required
def album_posts(request, album_id=None):
    profile_user = request.user

    if album_id:
        try:
            current = Albums.objects.get(id=album_id)
            items = current.posts.all()
            #getting news_feed for Post Objects
            items = [x.get_news() for x in items]
        except:
            items = []

    return render_to_response(
        'profile/album_posts.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
            'items' : items,
        },
        RequestContext(request)
    )

@login_required
def album_create(request):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'album_name' in request.POST:
        data = {'status':'OK'}
        album, created = Albums.objects.get_or_create(name=request.POST['album_name'], user = request.user)
        if created:
            data['html'] = render_to_string('profile/album.html',
                {
                    'album' : album,
                }, context_instance=RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def album_postion(request):
    data = {'status':'OK'}
    if request.method == 'POST' and 'album_id' in request.POST:
        album_id = request.POST.get('album_id',None)
        pos_bgn = request.POST.get('position_bgn',None)
        pos_end = request.POST.get('position_end',None)
        try:
            current = Albums.objects.get(id=album_id)
            current.position = int(pos_end)
            if request.user == current.user:
                current.save()
                if pos_bgn < pos_end:
                    albums = Albums.objects.filter(position__gte=pos_bgn, position__lte=pos_end, user=request.user).exclude(id=current.id)
                    albums.update(position=F('position') - 1)
                elif pos_bgn > pos_end:
                    albums = Albums.objects.filter(position__gte=pos_end, position__lte=pos_bgn, user=request.user).exclude(id=current.id)
                    albums.update(position=F('position') + 1)
                else:
                    pass
        except:
            pass
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def change_album_name(request):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'album_id' in request.POST:
        album_id = request.POST.get('album_id',None)
        album_name = request.POST.get('album_name',None)
        try:
            current = Albums.objects.get(id=album_id)
            current.name = album_name.strip()
            if request.user == current.user:
                current.save()
                data['status']='OK'
        except:
            pass
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def delete_album(request):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'album_id' in request.POST:
        album_id = request.POST.get('album_id',None)
        try:
            current = Albums.objects.get(id=album_id)
            if request.user == current.user:
                current.delete()
                data['status']='OK'
        except:
            pass
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def settings(request):
    changed = False
    active = 'basics'
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
            #Pop-up right window
            if request.POST.get('form_name') == 'privacy':
                active = 'privacy'
            else:
                active = 'basics'
    else:

        form = UserInfoForm(instance=request.user,initial = request.user.get_options())
        form_pass = PasswordChangeForm(user=request.user)

    return render_to_response(
        'profile/settings.html',
        {
            'form' : form,
            'form_pass' : form_pass,
            'changed' : changed,
            'active' : active,
        },
        RequestContext(request)
    )

@login_required
def delete_profile(request):
    data = {'status':'FAIL'}
    if request.method == 'POST':
        if 'confirm_password' in request.POST:
            password = request.POST['confirm_password']
            if check_password(password, request.user.password):
                request.user.user_ptr.delete()
                data['status'] = 'OK'
                data['redirect'] = reverse('account.views.home')
            else:
                data['message'] = 'Wrong password'
        else:
            data['message'] = 'Enter password'
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def related_users(request,username=None):
    if not username:
        profile_user = request.user
    else:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404()

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
        if filter_name == 'Friends':
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
        if filter_name == 'Friends':
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
