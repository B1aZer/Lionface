from django.contrib.auth.decorators import login_required
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from tags.models import Tag
import re

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def add_tag(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'tags' in request.POST:
        tags = request.POST['tags']
        tags = tags.replace('#','')
        tags = re.split(r'[,; ]', tags)

        for tag in tags:
            if tag:
                try:
                    tag = Tag.objects.get(name=tag)
                    request.user.tags.add(tag)
                except ObjectDoesNotExist:
                    request.user.tags.create(name=tag)

        data['tags']=tags

    return HttpResponse(json.dumps(data), "application/json")
