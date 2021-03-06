from django.http import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from forms import *
import public.views
import profile.views
from decorators import *
from django.contrib.auth.decorators import login_required
from models import *
from notification.models import Notification
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
from django.utils import timezone


@public_required
def signup(request, template='public/home.html'):
    signup = True
    if request.method == 'POST':
        form = SignupForm(prefix='signup', data=request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user_profile = getattr(new_user, 'userprofile', None)
            #saving full name
            if new_user_profile:
                new_user_profile.optional_name = form.cleaned_data['full_name']
                new_user_profile.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if new_user is not None:
                auth_login(request, new_user)
                return redirect('home')
            raise HttpResponseServerError()
    else:
        form = SignupForm(prefix='signup')
        signup = False

    return render(request,
        template,
        {
            'login_form': LoginForm(prefix='login'),
            'signup_form': form,
            'signup': signup,
            'signup_page': True
        }
    )


@public_required
def login(request, template_name='public/home.html'):
    if request.method == 'POST':
        form = LoginForm(prefix='login', data=request.POST)
        if form.is_valid():
            user = form.login(request)
            if user is not None:
                # timezone
                usp = user.userprofile
                usp.timezone = form.cleaned_data.get('tzone')
                usp.save()
                path = request.POST.get('next', None)
                if path:
                    return redirect(path)
                else:
                    return redirect('home')
        form.error_message = "There is an error with your login credentials."
    else:
        form = LoginForm(prefix='login')

    return render(request,
        template_name,
        {
            'login_form': form,
            'signup_form': SignupForm(prefix='signup')
        }
    )


@active_required
def home(request):
    # If the user isn't signed in, forward to the public view.
    if not request.user.is_authenticated():
        act = request.GET.get('act')
        if act == 'signup':
            return signup(request)
        return public.views.home(request)

    # Redirect to the user's feed
    return redirect(profile.views.feed, username=request.user)


def pending(request):
    return render(request,
        'registration/pending_email_verification.html',
        {
        }
    )


@active_required
@login_required
def follow(request):
    if 'user' in request.GET:
        try:
            following = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.add_following(following)
    return HttpResponse(json.dumps({'status': 'OK'}), "application/json")


@active_required
@login_required
def unfollow(request):
    if 'user' in request.GET:
        try:
            following = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.remove_following(following)
    return HttpResponse(json.dumps({'status': 'OK'}), "application/json")


@active_required
@login_required
def friend_add(request):
    if 'user' in request.GET:
        try:
            friend = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        req, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=friend)
        req.save()
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    raise Http404()


@active_required
@login_required
def friend_remove(request):
    if 'user' in request.GET:
        try:
            friend = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.friends.remove(friend)
        if friend in request.user.get_following_blocked():
            request.user.activate_following(friend)
        if friend in request.user.get_followers_blocked():
            request.user.activate_follower(friend)
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    raise Http404()


@active_required
@login_required
def friend_accept(request, request_id):
    try:
        request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        request.accept()
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    except FriendRequest.DoesNotExist:
        raise Http404()
    raise Http404()


@active_required
@login_required
def friend_decline(request, request_id):
    try:
        request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        request.decline()
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    except FriendRequest.DoesNotExist:
        raise Http404()
    raise Http404()


@active_required
@login_required
def hide_friend(request):
    data = {'status': 'FAIL'}
    user_id = request.POST.get('user', None)
    try:
        user = UserProfile.objects.get(id=user_id)
    except:
        raise Http404
    if request.user != user:
        request.user.hidden.add(user)
        request.user.save()
        data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")


@active_required
@login_required
def filter_add(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'filter_name' in request.POST:
        filter_name = request.POST['filter_name']
        single = request.POST.get('single', None)
        if single:
            request.user.filters = ''
            request.user.save()
            # deactivate all tags
            request.user.user_tag_set.update(active=False)

        filters = request.user.filters.split(',')
        if filter_name == 'Friends':
                # update comet date
                request.session['feed_date_F'] = timezone.now()
                if 'F' not in filters:
                    filters.append('F')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Following':
                request.session['feed_date_W'] = timezone.now()
                if 'W' not in filters:
                    filters.append('W')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Businesses':
                request.session['feed_date_B'] = timezone.now()
                if 'B' not in filters:
                    filters.append('B')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Nonprofits':
                request.session['feed_date_N'] = timezone.now()
                if 'N' not in filters:
                    filters.append('N')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
    return HttpResponse(json.dumps(data), "application/json")


@active_required
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
        if filter_name == 'Following':
                if 'W' in filters:
                    filters.remove('W')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Businesses':
                if 'B' in filters:
                    filters.remove('B')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
        if filter_name == 'Nonprofits':
                if 'N' in filters:
                    filters.remove('N')
                    filters = ','.join(filters)
                    request.user.filters = filters
                    request.user.save()
    return HttpResponse(json.dumps(data), "application/json")


@active_required
@login_required
def relation_accept(request, relation_id):
    data = {'status': 'OK'}
    try:
        relation = RelationRequest.objects.get(id=relation_id)
    except:
        raise Http404
    # delete notifications
    post_type = ContentType.objects.get_for_model(relation)
    notf = Notification.objects.filter(content_type__pk=post_type.id, object_id=relation.id)
    notf.delete()

    relation.accept()
    return HttpResponse(json.dumps(data), "application/json")


@active_required
@login_required
def relation_decline(request, relation_id):
    data = {'status': 'OK'}
    try:
        relation = RelationRequest.objects.get(id=relation_id)
    except:
        raise Http404
    # delete notifications
    post_type = ContentType.objects.get_for_model(relation)
    notf = Notification.objects.filter(content_type__pk=post_type.id, object_id=relation.id)
    notf.delete()

    relation.decline()
    return HttpResponse(json.dumps(data), "application/json")


def resend_activation(request):
    if not request.user.is_active:
        redirect('/')
    site = Site.objects.get_current()
    not_sent = False
    try:
        registration_profile = request.user.registrationprofile_set.get()
        registration_profile.send_activation_email(site)
    except:
        not_sent = True

    return render(request,
        'registration/activation_sent.html',
        {
            'email': request.user.email,
            'not_sent': not_sent,
        }
    )


def change_email(request):
    return render(request,
        'registration/email_change.html',
        {
        }
    )


def save_email(request):
    data = {'status': 'OK'}
    email = request.POST.get('email')
    if not email:
        raise Http404
    request.user.email = email.strip()
    try:
        validate_email( email )
        request.user.save()
    except:
        data['status'] = 'FAIL'
        return render(request,
            'registration/email_change.html',
            {
                'email_error':True
            }
        )
    #return HttpResponse(json.dumps(data), "application/json")
    return redirect('account.views.pending')
