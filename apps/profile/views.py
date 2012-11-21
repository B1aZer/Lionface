from django.http import *
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string

from account.models import UserProfile
from images.models import Image, ImageComments
from messaging.models import Messaging
from post.models import Albums
from notification.models import Notification

from messaging.forms import MessageForm
from images.forms import ImageForm
from .forms import *

from django.db.models import F

from .decorators import unblocked_users, default_user
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password

from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

from PIL import Image as pilImage

try:
    import json
except ImportError:
    import simplejson as json


@login_required
def feed(request, username):
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
        },
        RequestContext(request)
    )


@login_required
@unblocked_users
def images(request, username, rows_show=4):
    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

    is_visible = profile_user.check_visiblity('profile_image', request.user)
    if not is_visible:
        raise Http404

    ctype = ContentType.objects.get_for_model(UserProfile)
    qs = Image.objects.filter(owner_type=ctype, owner_id=profile_user.id)
    manage_perm = request.user == profile_user

    if request.method == 'POST' and manage_perm:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(profile_user)
            image.make_activity()
            try:
                pil_object = pilImage.open(image.image.path)
                w, h = pil_object.size
                x, y = 0, 0
                if w > h:
                    x, y, w, h = int((w-h)/2), 0, h, h
                elif h > w:
                    x, y, w, h = 0, int((h-w)/2), w, w
                new_pil_object = pil_object \
                    .crop((x, y, x+w, y+h)) \
                    .resize((200, 200))
                new_pil_object.save(image.image.thumb_path)
            except:
                pass
            return redirect('profile.views.images', username=profile_user.username)
    else:
        form = ImageForm()

    return render_to_response(
        'profile/images.html',
        {
            'profile_user': profile_user,
            'form': form,
            'image_rows': qs.get_rows(0, rows_show),
            'total_rows': qs.total_rows(),
            'photos_count': qs.count(),
            'manage_perm': manage_perm,
        },
        RequestContext(request)
    )


@login_required
@unblocked_users
def images_ajax(request, username):
    if not request.is_ajax():
        raise Http404

    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

    is_visible = profile_user.check_visiblity('profile_image', request.user)
    if not is_visible:
        raise Http404

    method = request.REQUEST.get('method', None)
    if method not in ['more', 'activity', 'delete', 'change_position']:
        raise Http404

    ctype = ContentType.objects.get_for_model(UserProfile)
    qs = Image.objects.filter(owner_type=ctype, owner_id=profile_user.id)
    manage_perm = request.user == profile_user

    if method in ['activity', 'delete', 'change_position'] and not manage_perm:
        raise Http404

    data = {}
    try:
        if method == 'more':
            try:
                row = int(request.REQUEST.get('row', None))
            except (TypeError, ValueError), e:
                return HttpResponseBadRequest('Bad row was received.')
            data['total_rows'] = qs.total_rows()
            if row >= data['total_rows']:
                return HttpResponseBadRequest('Row larger than total_rows.')
            data['html'] = render_to_string('images/li.html', {
                'rows': qs.get_row(row),
                'manage_perm': manage_perm,
            }, context_instance=RequestContext(request))
        elif method == 'activity':
            try:
                image = qs.get(pk=request.REQUEST.get('pk', None))
            except Image.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            image.make_activity()
            profile_user = UserProfile.objects.get(pk=profile_user.pk)
        elif method == 'delete':
            try:
                row = int(request.REQUEST.get('row', None)) - 1
            except (TypeError, ValueError), e:
                return HttpResponseBadRequest('Bad row was received.')
            try:
                image = qs.get(pk=request.REQUEST.get('pk', None))
            except UserImages.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            image.delete()
            if image.activity == True:
                profile_user = UserProfile.objects.get(pk=profile_user.pk)
            if row < qs.total_rows():
                image_row = qs.get_row(row)[-1:]
                manage_perm = request.user == profile_user
                data['html'] = render_to_string('images/li.html', {
                    'rows': image_row,
                    'manage_perm': manage_perm,
                }, context_instance=RequestContext(request))
        elif method == 'change_position':
            try:
                obj = qs.get(pk=request.REQUEST.get('pk', None))
                if obj.activity:
                    return HttpResponseBadRequest('Image with pk is actively.')
            except Image.DoesNotExist as e:
                return HttpResponseBadRequest('Bad pk was received.')
            try:
                instead = qs.get(pk=request.REQUEST.get('instead', None))
                if instead.activity:
                    return HttpResponseBadRequest('Image with instead is actively.')
            except Image.DoesNotExist as e:
                return HttpResponseBadRequest('Bad instead was received.')
            obj.change_position(obj.rating, instead.rating)
        else:
            raise Http404
        data['positions'] = qs.get_positions()
        data['thumb_src'] = '/' + profile_user.photo.thumb_name
        data['photos_count'] = qs.count()
    except Exception as e:
        data['status'] = 'fail'
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")


@login_required
@unblocked_users
def images_comments_ajax(request, username):
    if not request.is_ajax():
        raise Http404

    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

    is_visible = profile_user.check_visiblity('profile_image', request.user)
    if not is_visible:
        raise Http404

    method = request.REQUEST.get('method', None)
    if method not in ['create', 'list', 'delete']:
        raise Http404

    ctype = ContentType.objects.get_for_model(UserProfile)
    qs = Image.objects.filter(owner_type=ctype, owner_id=profile_user.id)
    manage_perm = request.user == profile_user

    try:
        image = qs.get(pk=request.REQUEST.get('pk', None))
    except Image.DoesNotExist as e:
        return HttpResponseBadRequest('Bad pk was received.')

    if method in ['delete'] and not manage_perm:
        raise Http404

    data = {}
    try:
        if method == 'create':
            try:
                message = request.REQUEST['message']
            except KeyError:
                return HttpResponseBadRequest("Comment wasn't received.")
            comment = ImageComments.objects.create(
                image=image,
                owner=request.user,
                message=message
            )
        elif method == 'list':
            pass
        elif method == 'delete':
            try:
                comment = image.comments.get(pk=request.REQUEST.get('comment_pk', None))
            except ImageComments.DoesNotExist as e:
                return HttpResponseBadRequest('Bad comment_pk was received.')
            comment.delete()
        else:
            raise Http404
        data['comments'] = render_to_string('images/li_comment.html', {
            'profile_user': profile_user,
            'image': image,
            'comments': image.comments.all(),
            'manage_perm': manage_perm,
        }, context_instance=RequestContext(request))
    except Exception as e:
        data['status'] = 'fail'
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")


#@login_required
@unblocked_users
#@default_user
def profile(request, username):
    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

    form_mess = MessageForm()
    form_mess.fields['content'].widget.attrs['rows'] = 7

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if request.user.is_authenticated() \
         and 'image' in request.POST \
         and form.is_valid():
            image = form.save(profile_user)
            image.make_activity()
            try:
                pil_object = pilImage.open(image.image.path)
                w, h = pil_object.size
                x, y = 0, 0
                if w > h:
                    x, y, w, h = int((w-h)/2), 0, h, h
                elif h > w:
                    x, y, w, h = 0, int((h-w)/2), w, w
                new_pil_object = pil_object \
                    .crop((x, y, x+w, y+h)) \
                    .resize((200, 200))
                new_pil_object.save(image.image.thumb_path)
            except:
                pass
            return redirect('profile.views.profile', username=profile_user.username)

        if 'message' in request.POST:
            form_mess = MessageForm(request.POST)
            if form_mess.is_valid():
                user_to = profile_user
                content = form_mess.cleaned_data['content']
                mess = Messaging(user=request.user,user_to=user_to,content=content)
                mess.save()
                return HttpResponseRedirect(request.path)
    else:
        form = ImageForm()
        

    if request.method == 'GET' and 'albums' in request.GET:
        """Albums view"""
        return render_to_response(
            'profile/albums.html',
            {
                'profile_user': profile_user,
                'form_mess' : form_mess,
                'albums' : request.user.albums_set.all().order_by('position'),
            },
            RequestContext(request)
        )

    return render_to_response(
        'profile/profile.html',
        {
            'profile_user': profile_user,
            'form' : form,
            'form_mess' : form_mess,
        },
        RequestContext(request)
    )


@login_required
@unblocked_users
def albums(request, username):
    """Albums view"""
    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

    return render_to_response(
        'profile/albums.html',
        {
            'profile_user': profile_user,
            'albums' : profile_user.albums_set.all().order_by('position'),
        },
        RequestContext(request)
    )

@login_required
@unblocked_users
def album_posts(request, username, album_id=None):
    try:
        profile_user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        raise Http404

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
            'items' : items,
        },
        RequestContext(request)
    )

@login_required
def album_create(request, username):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'album_name' in request.POST:
        data = {'status':'OK'}
        album, created = Albums.objects.get_or_create(name=request.POST['album_name'], user = request.user)
        if created:
            data['html'] = render_to_string('profile/album.html',
                {
                    'album': album,
                    'profile_user': request.user,
                }, context_instance=RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def album_postion(request, username):
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
def change_album_name(request, username):
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
def delete_album(request, username):
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
def settings(request, username):
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
def delete_profile(request, username):
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
def related_users(request,username):
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
                    'current_user': profile_user,
                    'users': list(set(users)),
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
def reset_picture(request, username):
    profile = request.user
    if profile != request.user:
        raise Http404
    UserImages.objects.filter(profile=profile).filter(activity=True) \
        .update(activity=False)
    profile.photo = [field.default
        for field in UserProfile._meta.fields if field.name == 'photo'
    ][0]
    profile.save()
    if request.META['HTTP_REFERER']:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return redirect('profile.views.profile', username=profile.username)

@login_required
@unblocked_users
def loves(request, username):
    data = {}
    if not username:
        profile_user = request.user
    else:
        try:
            profile_user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise Http404()

    pages = profile_user.get_loved()

    if request.method == 'GET' and 'ajax' in request.GET:
        if 'business' in request.GET and not 'nonprofit' in request.GET:
            pages = pages.filter(type='BS')
        if 'nonprofit' in request.GET and not 'business' in request.GET:
            pages = pages.filter(type='NP')

    if request.method == 'GET' and 'ajax' in request.GET:
        data['html'] = render_to_string('pages/pages_loves.html',
                {
                    'pages': pages,
                }, context_instance=RequestContext(request))
        return HttpResponse(json.dumps(data), "application/json")

    return render_to_response(
        'profile/loves.html',
        {
            'profile_user' : profile_user,
            'current_user' : profile_user,
            'pages' : pages,
        },
        RequestContext(request)
    )
