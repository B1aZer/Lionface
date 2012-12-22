from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from account.models import UserProfile
from post.models import ContentPost
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
            if owner_type == 'content post':
                post = get_object_or_404(ContentPost, id=owner_id)
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
                raise Http404
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
