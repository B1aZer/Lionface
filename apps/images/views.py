from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from account.models import UserProfile
from post.models import *
from .models import Image

try:
    import json
except ImportError:
    import simplejson as json


def notifications(request):
    # import pdb; pdb.set_trace()
    owner_id = request.REQUEST.get('owner_id', None)
    owner_type = request.REQUEST.get('owner_type', None)
    data = {}
    try:
        if owner_id:
            post = get_object_or_404(Post, id=owner_id)
            post = post.get_inherited()
            ctype = ContentType.objects.get_for_model(post)
            qs = Image.objects.filter(owner_type=ctype, owner_id=post.id)
            try:
                image_pk = request.REQUEST.get('pk', None)
                image = qs.get(pk=image_pk)
            except Image.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            data['owner'] = 'post'
            data['images_comments_ajax'] = reverse(
                'post_images_ajax_comments')
        else:
            ctype = ContentType.objects.get_for_model(UserProfile)
            qs = Image.objects.filter(owner_type=ctype, owner_id=request.user.id)
            try:
                image = qs.get(pk=request.REQUEST.get('pk', None))
            except Image.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            data['owner'] = 'user'
            data['images_comments_ajax'] = reverse(
                'profile.views.images_comments_ajax',
                args=(request.user.username,)
            )

        data['html'] = render_to_string('images/notifications.html', {
            'image': image,
            'owner': data['owner'],
        }, context_instance=RequestContext(request))
    except Exception as e:
        data['status'] = 'fail'
        print e
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")

def add_followings(request):
    data = {'status':'FAIL'}
    request_post = json.loads(request.raw_post_data)
    username = request_post.get('user')
    imagepk = request_post.get('imagepk')
    add = request_post.get('add')
    try:
        user = UserProfile.objects.get(username=username)
    except:
        raise Http404
    try:
        image = Image.objects.get(id=imagepk)
    except:
        raise Http404
    if add:
        image.following.add(user)
        data['status'] = 'OK'
        data['rem'] = False
    else:
        image.following.remove(user)
        data['status'] = 'OK'
        data['rem'] = True
    return HttpResponse(json.dumps(data), "application/json")

def del_followings(request):
    data = {'status':'FAIL'}
    return HttpResponse(json.dumps(data), "application/json")
