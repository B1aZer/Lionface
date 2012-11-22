from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from account.models import UserProfile
from .models import Image

try:
    import json
except ImportError:
    import simplejson as json


def notifications(request):
    ctype = ContentType.objects.get_for_model(UserProfile)
    qs = Image.objects.filter(owner_type=ctype, owner_id=request.user.id)
    try:
        image = qs.get(pk=request.REQUEST.get('pk', None))
    except Image.DoesNotExist:
        return HttpResponseBadRequest('Bad PK was received.')

    data = {}
    try:
        data['html'] = render_to_string('images/notifications.html', {
            'image': image,
        }, context_instance=RequestContext(request))
        data['images_comments_ajax'] = reverse(
            'profile.views.images_comments_ajax',
            args=(request.user.username,)
        )
    except Exception as e:
        data['status'] = 'fail'
        print e
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")
