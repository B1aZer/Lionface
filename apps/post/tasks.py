from celery.task import Task
from celery.registry import tasks
from celery.contrib import rdb


class UpdateNewsFeeds(Task):
    def run(self, post, user=None, **kwargs):
        from models import NewsItem, FriendPost, SharePost, ContentPost, PagePost
        #rdb.set_trace()
        if isinstance(post, FriendPost):
            ni, created = NewsItem.objects.get_or_create(user=post.user, post=post)
            ni, created = NewsItem.objects.get_or_create(user=post.friend, post=post)
        elif isinstance(post, ContentPost):
            ni, created = NewsItem.objects.get_or_create(user=post.user_to, post=post)
        elif isinstance(post, SharePost):
            ni, created = NewsItem.objects.get_or_create(user=post.user_to, post=post)
        elif isinstance(post, PagePost):
            users = post.page.get_lovers_active()
            for user in users:
                ni, created = NewsItem.objects.get_or_create(user=user, post=post)
        else:
            ni, created = NewsItem.objects.get_or_create(user=post.user_to, post=post)

tasks.register(UpdateNewsFeeds)


class DeleteNewsFeeds(Task):
    def run(self, post, user=None, **kwargs):
        from models import NewsItem, FriendPost
        #rdb.set_trace()
        post_wrapper = post
        if user:
            users = [user]
        else:
            users = post_wrapper.get_involved()
        for user in users:
            post_news = NewsItem.objects.filter(user=user, post=post_wrapper.post)
            if post_news:
                if not isinstance(post_news[0].post.get_inherited(), FriendPost):
                    post_news.delete()
                elif post_news[0].user == user:
                    post_news.delete()

tasks.register(DeleteNewsFeeds)

# Churns through the list of posts for the new friend and adds them to the news feed for this user.


class AddFriendToFeed(Task):
    def run(self, user, friend, **kwargs):
        from models import NewsItem
        #for post in Post.objects.filter(user=friend):
            #UpdateNewsFeeds.delay(post, user)
        for post in NewsItem.objects.filter(user=friend):
            UpdateNewsFeeds.delay(post.post.get_inherited(), user)

tasks.register(AddFriendToFeed)
