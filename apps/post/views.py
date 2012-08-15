from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import *

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def feed(request, user_id = None):
    items = request.user.get_news()
    if user_id:
        items = items.filter(post__user__id=user_id)
    
    return render_to_response(
        'post/_feed.html',
        {
            'items': items,
        },
        RequestContext(request)
    )

@login_required
def save(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'content' in request.POST:
        post = ContentPost(content = request.POST['content'], user = request.user)
        if 'type' in request.POST:
            post.type = request.POST['type']
        else: post.type = 'P'
        post.save()
        
        data['post_id'] = post.id
        
    return HttpResponse(json.dumps(data), "application/json")