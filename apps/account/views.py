from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import redirect
from forms import *
import public.views
import profile.views
from decorators import *
from django.contrib.auth.decorators import login_required
from models import *
import json

@public_required
def signup(request):
    if request.method == 'POST':
        form = SignupForm(prefix='signup', data=request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if new_user is not None:
                auth_login(request, new_user)
                return redirect('home')
            raise HttpResponseServerError()
    else:
        form = SignupForm(prefix='signup')

    return render_to_response(
        'account/signup.html',
        {
            'login_form': LoginForm(prefix='login'),
            'signup_form': form
        },
        RequestContext(request)
    )

@public_required
def login(request, template_name='public/home.html'):
    if request.method == 'POST':
        form = LoginForm(prefix='login', data=request.POST)
        if form.is_valid():
            user = form.login(request)
            if user is not None:
                return redirect('home')
        form.error_message = "Invalid e-mail address and password provided."
    else: form = LoginForm(prefix='login')

    return render_to_response(
        template_name,
        {
            'login_form': form,
        },
        RequestContext(request)
    )

def home(request):
    # If the user isn't signed in, forward to the public view.
    if not request.user.is_authenticated(): return public.views.home(request)

    # Redirect to the user's feed
    return redirect(profile.views.feed)

@login_required
def follow(request):
    if 'user' in request.GET:
        try:
            following = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.add_following(following)
    return HttpResponse(json.dumps({'status': 'OK'}), "application/json")

@login_required
def unfollow(request):
    if 'user' in request.GET:
        try:
            following = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.remove_following(following)
    return HttpResponse(json.dumps({'status': 'OK'}), "application/json")

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

@login_required
def friend_remove(request):
    if 'user' in request.GET:
        try:
            friend = UserProfile.objects.get(id=request.GET['user'])
        except User.DoesNotExist:
            raise Http404()
        request.user.friends.remove(friend)
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    raise Http404()

@login_required
def friend_accept(request, request_id):
    try:
        request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        request.accept()
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    except FriendRequest.DoesNotExist:
        raise Http404()
    raise Http404()

@login_required
def friend_decline(request, request_id):
    try:
        request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        request.decline()
        return HttpResponse(json.dumps({'status': 'OK'}), "application/json")
    except FriendRequest.DoesNotExist:
        raise Http404()
    raise Http404()
