from django.db import models
from account.models import UserProfile
from tags.models import Tag

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.db.models.signals import post_save, post_delete
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.contenttypes.models import ContentType
from django.contrib import comments
from django.conf import settings

import re
from .utils import QuerySetManager
from django.utils.safestring import mark_safe
from itertools import chain

from tasks import UpdateNewsFeeds

# import the logging library
import logging
logger = logging.getLogger(__name__)


class QuerySet(models.query.QuerySet):
    """Base QuerySet class for adding custom methods that are made
    available on both the manager and subsequent cloned QuerySets"""

    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls)



class CustomQuerySet(QuerySet):
    def get_news_post(self):
        """ getting news feed for post ids"""
        news = NewsItem.objects.filter(post_id__in=self.values_list('id', flat=True))
        return news


class Post(models.Model):
    user = models.ForeignKey(UserProfile,  related_name='user')
    user_to = models.ForeignKey(UserProfile,  related_name='user_to')
    following = models.ManyToManyField(UserProfile,  related_name='follows', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    shared = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    allow_commenting = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)
    album = models.ForeignKey('Albums', related_name="posts", on_delete=models.SET_NULL, null=True, blank=True)
    objects = CustomQuerySet.as_manager()

    # Function to attempt to return the inherited object for this item.
    def get_inherited(self):
        try: return self.friendpost
        except Exception: pass
        try: return self.contentpost
        except Exception: pass
        try: return self.sharepost
        except Exception: pass
        return self

    # Return a list of users who are involved with this post (i.e. should see it)
    def get_involved(self):
        return self.user.friends.all()

    def render(self):
        return self.get_inherited().render()

    def get_owner(self):
        try:
            original = self.get_inherited()
            if original._meta.verbose_name == 'share post':
                return original.user_to
        except:
            return False
        return original.user

    def get_type(self):
        try:
            original = self.get_inherited()
        except:
            return False
        return original._meta.verbose_name

    def get_post(self):
        return self

    def get_privacy(self):
        original = self.get_inherited()
        return original.privacy()

    def get_comment_settings(self):
        original = self
        return original.allow_commenting

    def get_share_settings(self):
        original = self
        return original.allow_sharing

    def get_album(self):
        return self.album

    def get_news(self, ids = None):
        if not ids:
            try:
                news_feed = NewsItem.objects.filter(post_id=self.id)
            except:
                logger.warning('more than 1 object')
                news_feed = []
        else:
            try:
                news_feed = NewsItem.objects.filter(post_id__in=ids)
            except:
                logger.warning('Error retrieving news posts')
                news_feed = []
        return news_feed

    def delete(self, *args, **kwargs):
        """We are checkig if post exist in any newsfeed,
        delete otherwise"""
        if self.newsitem_set.all():
            return
        else:
            super(Post, self).delete(*args, **kwargs)


class FriendPost(Post):
    friend = models.ForeignKey(UserProfile)

    def name(self):
        return self._meta.verbose_name

    def get_involved(self):
        return self.user.friends.all() | self.friend.friends.all()

    def render(self):
        return mark_safe("<a href='%s'>%s</a> and <a href='%s'>%s</a> are now friends." % (self.user.get_absolute_url(), self.user.get_full_name(), self.friend.get_absolute_url(), self.friend.get_full_name()))

    def privacy(self):
        return ""



class ContentPost(Post):
    content = models.CharField(max_length=5000)
    type = models.CharField(max_length=1)

    def get_involved(self):
        # TODO: Might want to make this everyone for completely public posts?
        # That might overload the news feed thing though.
        return self.user.friends.all() | UserProfile.objects.filter(id=self.user.id)

    def render(self):
        #from django.utils.html import escape
        import bleach
        from oembed.core import replace
        #import pdb;pdb.set_trace()
        def add_http(url):
            if re.search('http://',url):
                pass
            else:
                url = u"".join([u'http://', url])
            return url

        # Clean
        #self.content = bleach.clean(self.content,attributes={'a': ['href', 'rel', 'name'],})
        self.content = bleach.clean(self.content)
        # Embed videos
        self.content = replace(self.content,max_width=535,fixed_width=535)
        # Linkify 
        self.content = bleach.linkify(self.content,target='_blank',filter_url=add_http)

        return mark_safe("<a href='%s'>%s</a><br /><div class='post_content'> %s</div>" % (self.user.get_absolute_url(), self.user.get_full_name(), self.content))

    def get_id(self):
         return self.id

    def name(self):
        return self._meta.verbose_name

    @property
    def timestamp(self):
        return self.date

    @property
    def post(self):
        return self

    def get_post(self):
        return self.post_ptr

    def get_type(self):
        return self._meta.verbose_name

    def get_owner(self):
        return self.user

    def privacy(self):
        return self.type

    @property
    def get_privacy(self):
        return self.privacy



class SharePost(Post):
    content = models.TextField(null=True)
    id_news = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def name(self):
        return self._meta.verbose_name

    def privacy(self):
        return getattr(self.content_object,'type',"")

    def get_original_post(self):
        """Return last shared object(child)"""
        try:
            original = NewsItem.objects.get(id=self.id_news)
            original = original.post.get_inherited()
        except NewsItem.DoesNotExist:
            original = False
        except:
            original = False
        return original

    def get_owner(self):
        return self.user_to

    def render(self):
        #import pdb;pdb.set_trace()
        return mark_safe("""<a href='%s'>%s</a> <span style='color: #AAA;'>shared a post from</span> <a href='%s'>%s</a>
                            <div class='share_content'>%s</div>""" % (self.user_to.get_absolute_url(), self.user_to.get_full_name(), self.user.get_absolute_url(), self.user.get_full_name(), self.content))


class CustomQuerySet(QuerySet):
    def get_public_posts(self, user=None):
        if not user:
            return [x for x in self if x.get_privacy == 'P']
        else:
            return [x for x in self if x.get_privacy == 'P' or (x.get_privacy == 'F' and x.post.user.has_friend(user)) or (x.get_privacy == 'F' and x.post.user == user) or x.get_privacy == '']
    def get_tagged_posts(self,tags):
        #import pdb;pdb.set_trace()
        tagged_posts = [x for x in self if x.post.tags.filter(name__in=tags)]
        if tagged_posts:
            self = list(chain(self, tagged_posts))
        return self
    def remove_similar(self):
        duplicates = []
        ids = []
        items = []
        for item in self:
            if item.post.id in items:
                duplicates.append(item.post.id)
                ids.append(item.id)
            items.append(item.post.id)
        if ids:
            for id_item in ids:
                self = self.exclude(id=id_item)
        return self
    def remove_to_other(self):
        for item in self:
            if isinstance(item.post.get_inherited(), ContentPost):
                if item.post.user <> item.post.user_to:
                    self = self.exclude(id=item.id)
        return self
    def filter_blocked(self, user=None):
        if user and user.get_blocked():
            for item in self:
                if item.get_owner() in user.get_blocked():
                    self = self.exclude(id=item.id)
        return self


class NewsItem(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post)
    hidden = models.BooleanField(default=False)
    #objects = NewsManager()
    #objects = QuerySetManager(CustomQuerySet)
    objects = CustomQuerySet.as_manager()

    class Meta:
        unique_together = ("user", "post")

    def render(self):
        return self.post.get_inherited().render()

    def name(self):
        return self.post.get_inherited().name()

    def shared(self):
        return self.post.shared

    def get_involved(self):
        # TODO: Might want to make this everyone for completely public posts?
        # That might overload the news feed thing though.
        return self.user.friends.all() | UserProfile.objects.filter(id=self.user.id)

    def get_id(self):
         original = self.post.get_inherited()
         return original.id

    def get_type(self):
        try:
            original = self.post.get_inherited()
        except:
            return False
        return original._meta.verbose_name

    def get_owner(self):
        try:
            original = self.post.get_inherited()
            if original._meta.verbose_name == 'share post':
                return original.user_to
        except:
            return False
        return original.user

    @property
    def get_privacy(self):
        original = self.post.get_inherited()
        return original.privacy()

    def get_comment_settings(self):
        original = self.post
        return original.allow_commenting

    def get_share_settings(self):
        original = self.post
        return original.allow_sharing

    def get_post(self):
        return self.post

    def get_album(self):
        return self.post.album

    def get_comment_counter(self, user=None):
        value = comments.get_model().objects.filter(
        content_type = ContentType.objects.get_for_model(self),
        object_pk = self.pk,
        site__pk = settings.SITE_ID
        ).exclude(user__in=user.get_blocked()).count()
        return value

    @property
    def timestamp(self):
        return self.date

def update_news_feeds(sender, instance, created, **kwargs):
    if created:
        UpdateNewsFeeds.delay(instance.get_inherited())
post_save.connect(update_news_feeds, sender=FriendPost)
post_save.connect(update_news_feeds, sender=ContentPost)
post_save.connect(update_news_feeds, sender=SharePost)

def delete_news_feeds(sender, instance, **kwargs):
    """Deletes original post"""
    try:
        post = instance.post
        post.delete()
    except ObjectDoesNotExist:
        pass
post_delete.connect(delete_news_feeds, sender=NewsItem)
#post_delete.connect(delete_news_feeds, sender=ContentPost)

def change_default_settings(sender, instance, created, **kwargs):
    if created:
        instance.allow_commenting = not instance.user.check_option('comment_default','Disabled')
        instance.allow_sharing = not instance.user.check_option('share_default','Disabled')
        instance.save()
post_save.connect(change_default_settings, sender=ContentPost)
post_save.connect(change_default_settings, sender=SharePost)

class Albums(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(blank = True, null = True)

    def get_count(self):
        try:
            return self.posts.count()
        except:
            return 0

def change_album_postion(sender, instance, created, **kwargs):
    if created:
        #getting max position
        max_pos = Albums.objects.filter(user=instance.user).order_by("-position")[0].position
        if max_pos is not None:
            instance.position = max_pos + 1
            instance.save()
        else:
            instance.position = 0
            instance.save()
post_save.connect(change_album_postion, sender=Albums)

def change_album_postion_ondelete(sender, instance, **kwargs):
    albums = Albums.objects.filter(position__gt=instance.position,user=instance.user)
    if albums.count() > 0:
        albums.update(position=F('position') - 1)
post_delete.connect(change_album_postion_ondelete, sender=Albums)


