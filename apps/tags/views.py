from django.contrib.auth.decorators import login_required
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from tags.models import *
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
                    tag_obj = request.user.user_tag_set.get(name__iexact=tag)
                    if not tag_obj in request.user.user_tag_set.all() and len(request.user.user_tag_set.all()) < 7:
                        request.user.user_tag_set.add(tag_obj)
                        applied.append(tag)
                except ObjectDoesNotExist:
                    if len(request.user.user_tag_set.all()) < 7:
                        request.user.user_tag_set.create(name=tag)
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
            tag = request.user.user_tag_set.get(name__iexact=tag_name)
        except ObjectDoesNotExist:
            data = {'status': 'tag not found'}
            return HttpResponse(json.dumps(data), "application/json")
        except MultipleObjectsReturned:
            tags = request.user.user_tag_set.filter(name__iexact=tag_name)
            tags.delete()
        #request.user.user_tag_set.remove(tag)
        tag.delete()
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def deactivate(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'tag_name' in request.POST:
        tag_name = request.POST['tag_name']
        try:
            tag = request.user.user_tag_set.get(name=tag_name)
        except ObjectDoesNotExist:
            data = {'status': 'tag not found'}
            return HttpResponse(json.dumps(data), "application/json")
        tag.active = False
        tag.save()
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def activate(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'tag_name' in request.POST:
        tag_name = request.POST['tag_name']
        try:
            tag = request.user.user_tag_set.get(name=tag_name)
        except ObjectDoesNotExist:
            data = {'status': 'tag not found'}
            return HttpResponse(json.dumps(data), "application/json")
        tag.active = True
        tag.save()
    return HttpResponse(json.dumps(data), "application/json")


