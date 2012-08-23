from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext,loader
import datetime

from models import *
from account.models import UserProfile
from tasks import UpdateNewsFeeds

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def feed(request, user_id = None):
    #import pdb;pdb.set_trace()
    items = request.user.get_news()
    if not user_id:
        user_id = request.user.id
        items = request.user.get_messages()
    else:
        #show messages adressed to user
        items = items.filter(post__user_to=user_id)
    if not request.user.has_friend(UserProfile.objects.get(id=user_id)) and int(request.user.id) <> int(user_id):
        items = items.filter(post__contentpost__type="P")
    return render_to_response(
        'post/_feed.html',
        {
            'items': items,
        },
        RequestContext(request)
    )

@login_required
def timeline(request,post_num=5):
    items = request.user.get_news()[post_num:5]
    return render_to_response(
        'post/_timeline.html',
        {
            'items': items,
        },
        RequestContext(request)
    )

@login_required
def save(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'content' in request.POST:
        if 'profile_id' in  request.POST:
            user_to = UserProfile.objects.get(id=request.POST['profile_id'])
        post = ContentPost(content = request.POST['content'], user = request.user , user_to=user_to  )
        if 'type' in request.POST:
            post.type = request.POST['type']
        else: post.type = 'P'
        post.save()

        data['post_id'] = post.id
        #import pdb;pdb.set_trace()


        t = loader.get_template('post/_feed.html')
        #c = RequestContext(request, {'items': NewsItem.objects.filter(post_id=data['post_id']) })
        # this is not working because celery is not so fast
        new_post = post
        #new_post.id = post.newsitem_set.all()[0].id
        c = RequestContext(request, {'items': [new_post],
                                    'del_false' : True})
        data['html'] = t.render(c)

    return HttpResponse(json.dumps(data), "application/json")

@login_required
def delete(request, post_id = None):
    #TODO can not delete after update
    #import pdb;pdb.set_trace()
    data = {'status': 'OK'}
    if request.method == 'GET' and 'type' in request.GET:
        post_type = request.GET['type']
        if post_type == 'content post':
            post_news = ContentPost.objects.get(id=post_id)
            #post_news.delete()
            DeleteNewsFeeds.delay(post_news)
            return HttpResponse(json.dumps(data), "application/json")
    if post_id:
        post = NewsItem.objects.get(id=post_id)
        DeleteNewsFeeds.delay(post)
        #post.delete()
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def share(request, post_id = None):
    data = {'status': 'OK'}
    if post_id:
        post = NewsItem.objects.get(id=post_id)
        post_type = post.post.get_inherited()
        if isinstance(post_type, SharePost):
            shared = SharePost(user = post.user , user_to=request.user , content = post_type.content, id_news = post_type.id_news )
            post = post_type.get_original_post().post.get_inherited()
            post.shared += 1
            post.save()
            shared.save()
        else:
            post = SharePost(user = post.user , user_to=request.user , content = post.render(), id_news = post.id )
            post_type.shared +=1
            post_type.save()
            post.save()
    return HttpResponse(json.dumps(data), "application/json")

