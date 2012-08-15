from celery.task import Task
from celery.registry import tasks

class UpdateNewsFeeds(Task):
    def run(self, post, user=None, **kwargs):
        from models import NewsItem
        if user: users = [user]
        else: users = post.get_involved()
        for user in users:
            ni, created = NewsItem.objects.get_or_create(user=user, post=post)
        
tasks.register(UpdateNewsFeeds)

# Churns through the list of posts for the new friend and adds them to the news feed for this user.
class AddFriendToFeed(Task):
    def run(self, user, friend, **kwargs):
        from models import Post, NewsItem
        for post in Post.objects.filter(user=friend):
            UpdateNewsFeeds.delay(post, user)

tasks.register(AddFriendToFeed)