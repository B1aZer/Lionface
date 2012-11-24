from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext,loader

from .models import *
from account.models import UserProfile
from tags.models import Tag

from tasks import DeleteNewsFeeds

from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import get_object_or_404
from django.contrib import comments

from itertools import chain


try:
    import json
except ImportError:
    import simplejson as json


def feed(request, user_id = None):
    data = {}
    news_feed_flag = False
    #news feed
    if not user_id:
        page_type = 'news_feed'
        news_feed_flag = True
        user_id = request.user.id
        filters = request.user.filters.split(',')
        items = request.user.get_messages() \
                .remove_page_posts() \
                .remove_similar() \
                .remove_to_other() \
                .filter_blocked(user=request.user) \
                .get_public_posts(request.user)
        tags = request.user.user_tag_set.all()
        if tags:
            tags = [x.name.upper() for x in tags if x.active]
            tagged_posts = Post.objects.all()
            try:
                tagged_posts = [x
                        for x in tagged_posts
                            for y in x.tags.all()
                                if y.name.upper() in tags]
            except Post.DoesNotExist:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning('Error in retrirving Post')
            items = list(chain(items, tagged_posts))
            items = list(set(items))
            items = sorted(items,key=lambda post: post.date, reverse=True)
        # adding page filter here, since we need to extend the query
        if 'B' in filters:
            business_pages = NewsItem.objects.get_business_feed(request.user)
            items = list(chain(items, business_pages))
            items = list(set(items))
            items = sorted(items,key=lambda post: post.date, reverse=True)
        if 'N' in filters:
            nonprofit_pages = NewsItem.objects.get_nonprofit_feed(request.user)
            items = list(chain(items, nonprofit_pages))
            items = list(set(items))
            items = sorted(items,key=lambda post: post.date, reverse=True)
    else:
        page_type = 'profile_feed'
        #items = NewsItem.objects.get_profile_wall(request.user).order_by('-date')
        items = NewsItem.objects.filter(hidden=False).order_by('date').reverse()
        # show messages adressed to user
        items = items.filter(user=user_id)
        # remove page posts
        items = items.remove_page_posts()
        # remove blocked
        if not request.user.is_anonymous:
            if request.user.get_blocked():
                items = items.filter_blocked(user=request.user)
        # privacy
        if request.user.id <> int(user_id):
            items = items.get_public_posts(request.user)
    #import pdb;pdb.set_trace()
    #if not request.user.has_friend(UserProfile.objects.get(id=user_id)) and int(request.user.id) <> int(user_id):
        #items = items.get_public_posts()

    # PAGINATION #
    paginator = Paginator(items, 7)
    items = paginator.page(1)

    if request.method == 'GET':
        page = request.GET.get('page', None)
        if page:
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                items = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                items = paginator.page(paginator.num_pages)
        else:
            page = 1

    data['html'] = loader.render_to_string(
        'post/_feed.html',
        {
            'items': items,
            'news_feed': news_feed_flag,
            'page': page,
            'page_type': page_type,
        },
        RequestContext(request)
    )

    data['page'] = page

    return HttpResponse(json.dumps(data), "application/json")


@login_required
def love(request):
    try:
        post = Post.objects \
            .select_related() \
            .get(pk=request.REQUEST.get('pk', None))
    except Post.DoesNotExist:
        return HttpResponseBadRequest('Bad PK was received.')

    data = {}
    try:
        if request.user.posts_loved.filter(pk=post.pk).count():
            post.loves -= 1
            post.save()
            request.user.posts_loved.remove(post)
            data['type'] = 'down'
        else:
            post.loves += 1
            post.save()
            request.user.posts_loved.add(post)
            data['type'] = 'up'
        data['count'] = post.loves
    except Exception as e:
        data['status'] = 'fail'
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def timeline(request,post_num=5):
    """Not sure if needed or not"""
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
        if post_type == 'page post':
            try:
                post = Post.objects.get(id=int(post_id))
                if request.POST['value'] == 'Follow':
                    request.user.follows.add(post)
                else:
                    request.user.follows.remove(post)
            except ObjectDoesNotExist:
                data['status'] = "FAIL"
                data['html'] = "Sorry no such post"
    return HttpResponse(json.dumps(data), "application/json")

def show(request):
    data = {'status': 'OK'}
    items = []
    if request.method == 'POST' and 'post_id' in request.POST:
        post_type = request.POST['post_type']
        post_id = request.POST['post_id']
        post_model = request.POST.get('post_model',None)

        if post_type == 'content post':
            try :
                cont_post = ContentPost.objects.get(id=int(post_id))
            except ObjectDoesNotExist:
                data['html'] = "Sorry no such post"
                return HttpResponse(json.dumps(data), "application/json")
            items = NewsItem.objects.filter(post=cont_post)

        if post_type == 'share post':
            try:
                share_post = SharePost.objects.get(id=int(post_id))
            except ObjectDoesNotExist:
                data['html'] = "Sorry no such post"
                return HttpResponse(json.dumps(data), "application/json")
            items = NewsItem.objects.filter(post=share_post)

        if post_type == 'comment post':
            if post_model == 'post_post':
                try:
                    items = Post.objects.filter(id=int(post_id))
                except ObjectDoesNotExist:
                    data['html'] = "Sorry no such post"
                    return HttpResponse(json.dumps(data), "application/json")
            else:
                try:
                    items = NewsItem.objects.filter(id=int(post_id))
                except ObjectDoesNotExist:
                    data['html'] = "Sorry no such post"
                    return HttpResponse(json.dumps(data), "application/json")

        if post_type in ('shared_multiple','profile_multiple'):
            from notification.models import Extra
            post_ids = [x.item_id for x in Extra.objects.filter(notification__id = post_id)]
            #post_ids = post_id.replace('[','').replace(']','').split(',')
            #post_ids = [x.id for x in SharePost.objects.filter(object_id = int(post_id))]
            if post_ids:
                items = Post.objects.get_news_post(post_ids)

        if len(items) > 0:
                t = loader.get_template('post/_feed.html')
                c = RequestContext(request,
                        {
                            'items': items,
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
        post_type = request.GET.get('type')
        post_model = request.GET.get('model',None)
        #this is news feed delete
        if 'user' in request.GET:
            owner = UserProfile.objects.get(id=int(request.GET['user']))
        else:
            owner = request.user
        #ownership is defined using template
        if post_model == 'post_newsitem':
            try:
                post = NewsItem.objects.get(id=post_id)
            except NewsItem.DoesNotExist:
                return HttpResponse(json.dumps(data), "application/json")
        #restore original count of shares
        if post_type == 'share post':
            original = post.post.get_inherited()
            if original.content_object:
                if original.content_object.shared != 0:
                    original.content_object.shared -= 1
                    original.content_object.save()
        if (post_type == 'page post' and post_model == 'post_pagepost') \
                or (post_type == 'feedback post' and post_model == 'post_feedbackpost') \
                or post_model == 'post_post':
            obj = Post.objects.get(id=post_id)
            obj.newsitem_set.delete()
            obj.delete()
            data['status'] = 'OK'
            return HttpResponse(json.dumps(data), "application/json")
        data['status'] = 'OK'
        DeleteNewsFeeds.delay(post,user=owner)
    return HttpResponse(json.dumps(data), "application/json")

@login_required
def share(request, post_id = None):
    data = {'status': 'OK'}
    if post_id:
        post_model = request.POST.get('post_model')
        if post_model in ('post_post','post_pagepost', 'post_feedbackpost'):
            post = Post.objects.get(id=post_id)
        else:
            post = NewsItem.objects.get(id=post_id)
        post_type = post.get_post().get_inherited()
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
                shared = SharePost(user = post_type.user , user_to=request.user , content = post_type.content, id_news = post_id, content_object = post_type )
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
        elif post_type == 'page post':
            post = get_object_or_404(PagePost, id=int(request.POST['post_id']))
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
                    data['album_url'] = reverse('profile.views.album_posts', kwargs={'album_id': alb_obj.id, \
                            'username':request.user.username})
            except:
                if post.album:
                    #remove post from album
                    post.album.posts.remove(post)
                data['album'] = ""
        else:
            if hasattr(post,'albums_set'):
                post.albums_set.clear()
    return  HttpResponse(json.dumps(data), "application/json")

@login_required
def test(request):
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



