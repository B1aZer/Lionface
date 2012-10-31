from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string

from account.models import UserProfile, UserImage
from messaging.models import Messaging
from post.models import Albums
from notification.models import Notification

from messaging.forms import MessageForm
from .forms import *

from django.db.models import F

from .decorators import unblocked_users, default_user
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password

from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def feed(request, username=None):
    return render_to_response(
        'profile/feed.html',
        {
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
@unblocked_users
def profile_image(request, username=None):
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404
    else:
        profile_user = request.user
    is_visible = profile_user.check_visiblity('profile_image', request.user)
    if not is_visible:
        raise Http404


    return render_to_response(
        'profile/image.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
        },
        RequestContext(request)
    )

@login_required
@unblocked_users
#@default_user
def profile(request, username='admin'):
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
                profile = UserProfile.objects.get(id=request.user.id)
                profile.photo = form.cleaned_data['photo']
                profile.save()
                image = UserImage.objects.create(
                    image=profile.photo,
                    owner=profile,
                    activity=True
                )
                profile.all_images.add(image)
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

    return

@login_required
@unblocked_users
def albums(request, username=None):
    """Albums view"""
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404
    else:
        profile_user = request.user

    return render_to_response(
        'profile/albums.html',
        {
            'profile_user': profile_user,
            'not_count': Notification.objects.filter(user=request.user,read=False).count(),
            'albums' : profile_user.albums_set.all().order_by('position'),
        },
        RequestContext(request)
    )

@login_required
@unblocked_users
def album_posts(request, username=None, album_id=None):
    if username != None:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404
    else:
        profile_user = request.user

    if album_id:
        try:
            from post.models import Post
            current = Albums.objects.get(id=album_id)
            items = Post.objects.filter(album_id = current.id)
            #getting news_feed for Post Objects
            items = items.get_news_post()
            items = items.get_public_posts(profile_user)
            items = sorted(items,key=lambda post: post.date, reverse=True)
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
def album_create(request, username=None):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'album_name' in request.POST:
        data = {'status':'OK'}
        album, created = Albums.objects.get_or_create(name=request.POST['album_name'], user = request.user)
        if created:
            data['html'] = render_to_string('profile/album.html',
                {
                    'album' : album,
                    'profile_user' : request.user,
                }, context_instance=RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def album_postion(request, username=None):
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
def change_album_name(request, username=None):
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
def delete_album(request, username=None):
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
def settings(request, username=None):
    changed = False
    active = 'basics'
    form = UserInfoForm(instance=request.user,initial = request.user.get_options())
    form_pass = PasswordChangeForm(user=request.user)
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
                if name == 'block_user':
                    #This is for blocked users
                    user_name = request.POST[name]
                    try:
                        user = UserProfile.objects.get(username=user_name)
                    except UserProfile.DoesNotExist:
                        continue
                    request.user.blocked.add(user)
            if form.is_valid():
                form.save()
            #Pop-up right window
            if request.POST.get('form_name') == 'privacy':
                active = 'privacy'
            else:
                active = 'basics'
        elif 'rem_hidden' in request.POST:
            hidden_users = request.POST.getlist('rem_hidden_list')
            for user_id in hidden_users:
                try:
                    user = UserProfile.objects.get(id=user_id)
                    request.user.hidden.remove(user)
                except:
                    continue
            #Pop-up right window
            if request.POST.get('form_name') == 'privacy':
                active = 'privacy'
            else:
                active = 'basics'
        elif 'rem_blocked' in request.POST:
            blocked_users = request.POST.getlist('rem_blocked_list')
            for user_id in blocked_users:
                try:
                    user = UserProfile.objects.get(id=user_id)
                    request.user.blocked.remove(user)
                except:
                    continue
            #Pop-up right window
            if request.POST.get('form_name') == 'privacy':
                active = 'privacy'
            else:
                active = 'basics'

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
def delete_profile(request, username=None):
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
@unblocked_users
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
            friends = profile_user.get_friends()
            if friends:
                friends = friends.exclude(id=request.user.id)
            users.extend(friends)
            data['html'] = [x.username for x in friends]
        if 'Following' in request.GET and profile_user.check_visiblity('following_list',request.user):
            following = profile_user.get_following_active(request.user)
            users.extend(following)
            data['html'] = [x.username for x in following]
        if 'Followers' in request.GET and profile_user.check_visiblity('follower_list',request.user):
            followers = profile_user.get_followers_active(request.user)
            users.extend(followers)
            data['html'] = [x.username for x in followers]
        if users:
            # custom ordering
            # the same as was ?
            users = sorted(users, key=lambda s: s.first_name)

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
def reset_picture(request, username=None):
    request.user.all_images.filter(activity=True).update(activity=False)
    request.user.photo = [field.default
        for field in UserProfile._meta.fields if field.name == 'photo'
    ][0]
    request.user.save()
    return redirect('profile.views.profile', username=request.user.username)
