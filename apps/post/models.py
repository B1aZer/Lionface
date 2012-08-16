from django.db import models
from account.models import UserProfile
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from tasks import UpdateNewsFeeds

class Post(models.Model):
    user = models.ForeignKey(UserProfile,  related_name='user')
    user_to = models.ForeignKey(UserProfile,  related_name='user_to')
    date = models.DateTimeField(auto_now_add=True)
    
    # Function to attempt to return the inherited object for this item.
    def get_inherited(self):
        try: return self.friendpost
        except Exception: pass
        try: return self.contentpost
        except Exception: pass
        return self
    
    # Return a list of users who are involved with this post (i.e. should see it)
    def get_involved(self):
        return self.user.friends.all()
        
    def render(self):
        return ""
    

class FriendPost(Post):
    friend = models.ForeignKey(UserProfile)

    def get_involved(self):
        return self.user.friends.all() | self.friend.friends.all()
        
    def render(self):
        return mark_safe("<a href='%s'>%s</a> is now friends with <a href='%s'>%s</a>" % (self.user.get_absolute_url(), self.user.get_full_name(), self.friend.get_absolute_url(), self.friend.get_full_name()))


class ContentPost(Post):
    content = models.TextField()
    type = models.CharField(max_length=1)
    
    def get_involved(self):
        # TODO: Might want to make this everyone for completely public posts?
        # That might overload the news feed thing though.
        return self.user.friends.all() | UserProfile.objects.filter(id=self.user.id)

    def render(self):
        from django.utils.html import escape
        return mark_safe("<a href='%s'>%s</a>: %s" % (self.user.get_absolute_url(), self.user.get_full_name(), escape(self.content)))

    @property
    def timestamp(self):
        return self.date  

class NewsItem(models.Model):
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post)
    hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "post")
        
    def render(self):
        return self.post.get_inherited().render()
    
    @property
    def timestamp(self):
        return self.date


def update_news_feeds(sender, instance, created, **kwargs):
    UpdateNewsFeeds.delay(instance.get_inherited())
post_save.connect(update_news_feeds, sender=Post)
post_save.connect(update_news_feeds, sender=FriendPost)
post_save.connect(update_news_feeds, sender=ContentPost)

# Logic is that as each post is saved, the news feed for each related user
# is rebuilt or amended by celery.  The news feed is basically a long timeline
# of all posts related to a user.  When friends are added or deleted, the
# feed is also heavily updated to add or remove relevant entries.
