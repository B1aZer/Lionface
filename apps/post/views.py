from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext,loader
import datetime

from models import *
from account.models import UserProfile
from tags.models import Tag
from post.models import NewsItem
from tasks import DeleteNewsFeeds
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

from django.shortcuts import get_object_or_404
from django.contrib import comments

from itertools import chain


try:
    import json
except ImportError:
    import simplejson as json

@login_required
def feed(request, user_id = None):
    filters = request.user.filters.split(',')
    items = request.user.get_news()
    #news feed
    if not user_id:
        user_id = request.user.id
        #items = request.user.get_messages().get_tagged_posts(tags)
        if 'F' in filters:
            items = request.user.get_messages().remove_similar().remove_to_other().get_public_posts(request.user)
        else:
            items = []
        tags = request.user.user_tag_set.all()
        if tags:
            tags = [x.name.upper() for x in tags if x.active]
            tagged_posts = NewsItem.objects.all()
            tagged_posts = [x for x in tagged_posts for y in x.post.tags.all() if y.name.upper() in tags ]
            #tagged_posts = NewsItem.objects.filter(post__tags__name__in=tags).order_by('-date')
            items = list(chain(items, tagged_posts))
            items = list(set(items))
            items = sorted(items,key=lambda post: post.date, reverse=True)
    else:
        #show messages adressed to user
        items = items.filter(user=user_id)
        if int(request.user.id) <> int(user_id):
            items = items.get_public_posts(request.user)
    #import pdb;pdb.set_trace()
    #if not request.user.has_friend(UserProfile.objects.get(id=user_id)) and int(request.user.id) <> int(user_id):
        #items = items.get_public_posts()

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

        #Tags
        hashtags = [word[1:] for word in request.POST['content'].split() if word.startswith('#')]

        for hashtag in hashtags:
            try:
                tag = Tag.objects.get(name__iexact=hashtag)
                post.tags.add(tag)
            except ObjectDoesNotExist:
                post.tags.create(name=hashtag)
            except MultipleObjectsReturned:
                tags = Tag.objects.filter(name__iexact=hashtag)
                tag = [p for p in tags if not hasattr(p, 'user_tag')]
                if tag:
                    post.tags.add(tag[0])

        data['post_id'] = post.id

        t = loader.get_template('post/_feed.html')
        new_post = post
        c = RequestContext(request, {'items': [new_post],
                                    'del_false' : True})
        data['html'] = t.render(c)

    return HttpResponse(json.dumps(data), "application/json")

def follow(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'post_id' in request.POST:
        post_type = request.POST['post_type']
        post_id = request.POST['post_id']
        if post_type == 'content post':
            try:
                cont_post = ContentPost.objects.get(id=int(post_id))
                if request.POST['value'] == 'Follow':
                    request.user.follows.add(cont_post)
                else:
                    request.user.follows.remove(cont_post)
            except ObjectDoesNotExist:
                data['status'] = "FAIL"
                data['html'] = "Sorry no such post"
        if post_type == 'share post':
            try:
                share_post = SharePost.objects.get(id=int(post_id))
                if request.POST['value'] == 'Follow':
                    request.user.follows.add(share_post)
                else:
                    request.user.follows.remove(share_post)
            except ObjectDoesNotExist:
                data['status'] = "FAIL"
                data['html'] = "Sorry no such post"
    return HttpResponse(json.dumps(data), "application/json")

def show(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'post_id' in request.POST:
        post_type = request.POST['post_type']
        post_id = request.POST['post_id']

        if post_type == 'content post':
            try :
                cont_post = ContentPost.objects.get(id=int(post_id))
            except ObjectDoesNotExist:
                data['html'] = "Sorry no such post"
                return HttpResponse(json.dumps(data), "application/json")

            post = NewsItem.objects.filter(post=cont_post)
            if len(post) > 0:
                t = loader.get_template('post/_feed.html')
                new_post = post
                c = RequestContext(request,
                        {
                            'items': new_post,
                            'notification':True,
                        })
                data['html'] = t.render(c)

        if post_type == 'share post':
            try:
                share_post = SharePost.objects.get(id=int(post_id))
            except ObjectDoesNotExist:
                data['html'] = "Sorry no such post"
                return HttpResponse(json.dumps(data), "application/json")

            post = NewsItem.objects.filter(post=share_post)
            if len(post) > 0:
                t = loader.get_template('post/_feed.html')
                new_post = post
                c = RequestContext(request,
                        {
                            'items': new_post,
                            'notification':True,
                        })
                data['html'] = t.render(c)

        if post_type == 'comment post':
            try:
                comm_post = NewsItem.objects.filter(id=int(post_id))
            except ObjectDoesNotExist:
                data['html'] = "Sorry no such post"
                return HttpResponse(json.dumps(data), "application/json")

            if len(comm_post) > 0:
                t = loader.get_template('post/_feed.html')
                c = RequestContext(request,
                        {
                            'items': comm_post,
                            'notification':True,
                        })
                data['html'] = t.render(c)

    return HttpResponse(json.dumps(data), "application/json")

@login_required
def delete_own_comment(request, message_id):
    #import pdb;pdb.set_trace()
    data = {'status': 'OK'}
    comment = get_object_or_404(comments.get_model(), pk=message_id,
            site__pk=settings.SITE_ID)
    if comment.user.userprofile == request.user or comment.content_object.user == request.user:
        comment.is_removed = True
        comment.save()
        data['status'] = 'removed'
        data['id'] = message_id
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def delete(request, post_id = None):
    data = {'status': 'FAIL'}
    if request.method == 'GET' and 'type' in request.GET and 'ajax' in request.GET:
        #this will fire on ajax post posting
        post_type = request.GET['type']
        if post_type == 'content post':
            post_news = ContentPost.objects.get(id=post_id)
            DeleteNewsFeeds.delay(post_news)
            data['status'] = 'OK'
            return HttpResponse(json.dumps(data), "application/json")
    if post_id:
        #this is news feed delete
        if 'user' in request.GET:
            owner = UserProfile.objects.get(id=int(request.GET['user']))
        else:
            owner = request.user
        #ownership is defined using template
        post = NewsItem.objects.get(id=post_id)
        #restore original count of shares
        post_type = request.GET.get('type')
        if post_type == 'share post':
            original = post.post.get_inherited()
            if original.content_object:
                if original.content_object.shared != 0:
                    original.content_object.shared -= 1
                    original.content_object.save()
        data['status'] = 'OK'
        DeleteNewsFeeds.delay(post,user=owner)
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def share(request, post_id = None):
    data = {'status': 'OK'}
    if post_id:
        post = NewsItem.objects.get(id=post_id)
        post_type = post.post.get_inherited()
        #if post already shared before
        if isinstance(post_type, SharePost):
            #post = post_type.get_original_post().post.get_inherited()
            post = post_type.content_object
            if post:
                #if origanl post was not deleted
                shared = SharePost(user = post_type.content_object.user , user_to=request.user , content = post_type.content, id_news = post_id, content_object = post )
                post.shared += 1
                post.save()
                shared.save()
            else:
                #if was
                shared = SharePost(user = post_type.user , user_to=request.user , content = post_type.content, id_news = post_type.id_news, content_object = post_type )
                post_type.shared +=1
                post_type.save()
                shared.save()
        else:
            #normal post
            post = SharePost(user = post_type.user , user_to=request.user , content = post.render(), id_news = post.id, content_object = post_type)
            post_type.shared +=1
            post_type.save()
            post.save()
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def toggle_privacy(request):
    data = {'status': 'FAIL'}
    if request.method == 'POST' and 'post_id' in request.POST and 'type' in request.POST:
        post_type = request.POST['type']
        post = get_object_or_404(ContentPost, id=int(request.POST['post_id']))
        if post_type == 'F':
            post.type = 'P'
        else:
            post.type = 'F'
        if post.user == request.user:
            post.save()
            data['status'] = 'OK'
    return  HttpResponse(json.dumps(data), "application/json")

@login_required
def change_settings(request):
    data = {'status': 'FAIL'}
    if request.method == 'POST' and 'post_id' in request.POST and 'post_type' in request.POST:
        post_type = request.POST['post_type']
        if post_type == 'content post':
            post = get_object_or_404(ContentPost, id=int(request.POST['post_id']))
        elif post_type == 'share post':
            post = get_object_or_404(SharePost, id=int(request.POST['post_id']))
        else:
            raise Http404
        data = {'status': 'OK'}
        if 'privacy_settings' in request.POST:
            privacy = request.POST['privacy_settings']
            if post.privacy() <> privacy[0].upper():
                post.type = privacy[0].upper()
                post.save()
                data['privacy'] = request.POST['privacy_settings']
        if 'comment_settings' in request.POST:
            post.allow_commenting = True
            post.save()
        else:
            post.allow_commenting = False
            post.save()
            data['commenting'] = 'turned off'
        if 'sharing_settings' in request.POST:
            post.allow_sharing = True
            post.save()
        else:
            post.allow_sharing = False
            post.save()
            data['sharing'] = 'turned off'
        if 'attach_to_album' in request.POST:
            album_id = request.POST['attach_to_album']
            post_album = post.album
            try:
                alb_obj = Albums.objects.get(id=album_id, user=request.user)
                if alb_obj <> post_album:
                    alb_obj.posts.add(post)
                    alb_obj.save()
                    data['album'] = alb_obj.name
            except ObjectDoesNotExist:
                if post.album:
                    #remove post from album
                    post.album.posts.remove(post)
                data['album'] = ""
        else:
            post.albums_set.clear()
    return  HttpResponse(json.dumps(data), "application/json")

@login_required
def test(request):
    #import pdb;pdb.set_trace()
    data = {'status': 'OK'}
    from django.contrib.comments.views.comments import post_comment
    commented = post_comment(request)

    #hack for finding comment's id
    location = commented.__getitem__('location')
    position = location.find('?c=') + 3
    com_id = location[position:]

    comment = get_object_or_404(comments.get_model(), pk=com_id,
            site__pk=settings.SITE_ID)

    t = loader.get_template('comments/single.html')
    c = RequestContext(request,
            {
                'comment': comment,
            })
    data['html'] = t.render(c)

    return HttpResponse(json.dumps(data), "application/json")



