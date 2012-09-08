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
    applied = []

    if request.method == 'POST' and 'tags' in request.POST:
        tags = request.POST['tags']
        tags = tags.replace('#','')
        tags = re.split(r'[,; ]', tags)

        for tag in tags:
            if tag:
                try:
                    tag_obj = Tag.objects.get(name=tag)
                    if not tag_obj in request.user.tags.all():
                        request.user.tags.add(tag_obj)
                        applied.append(tag)
                except ObjectDoesNotExist:
                    request.user.tags.create(name=tag)
                    applied.append(tag)
        tag_string = "".join(tags)
        if tag_string and applied:
            data['tags']=applied

    return HttpResponse(json.dumps(data), "application/json")

@login_required
def rem_tag(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'tag_name' in request.POST:
        tag_name = request.POST['tag_name']
        try:
            tag = Tag.objects.get(name=tag_name)
        except ObjectDoesNotExist:
            data = {'status': 'tag not found'}
            return HttpResponse(json.dumps(data), "application/json")
        request.user.tags.remove(tag)
    return HttpResponse(json.dumps(data), "application/json")
