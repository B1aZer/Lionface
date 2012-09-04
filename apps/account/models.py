from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.query import Q
from post.tasks import AddFriendToFeed

class FriendRequest(models.Model):
    from_user = models.ForeignKey('UserProfile', related_name='from_user')
    to_user = models.ForeignKey('UserProfile', related_name='to_user')
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    # Accept the friend request
    def accept(self):
        from notification.models import Notification
        from post.models import FriendPost
        self.from_user.friends.add(self.to_user)
        self.from_user.save()
        Notification(user=self.from_user, type='FA', other_user=self.to_user, content_object = self).save()
        FriendPost(user=self.from_user, friend=self.to_user, user_to=self.to_user).save()
        AddFriendToFeed.delay(self.from_user, self.to_user)
        AddFriendToFeed.delay(self.to_user, self.from_user)
        self.delete()

    # Decline the friend request
    def decline(self):
        self.delete()

class UserProfile(User):
    # Logic is if a friend is in the 'friends' collection then they are verified.
    # If there is an active FriendRequest then it's still pending.
    friends = models.ManyToManyField('self', related_name='friends')
    photo = models.ImageField(upload_to="uploads/images", verbose_name="Please Upload a Photo Image", default='images/noProfilePhoto.png')

    def has_friend(self, user):
        return self.friends.filter(id=user.id).count() > 0

    def has_friend_request(self, user):
        return FriendRequest.objects.filter(Q(from_user=self, to_user=user) | Q(to_user=self, from_user=user)).count() > 0

    # Returns a queryset for all news items this user can see in date order.
    def get_news(self):
        from post.models import NewsItem
        #return NewsItem.objects.filter(user=self, hidden=False).order_by('date').reverse()
        #User can see all public messages,
        #not only his
        return NewsItem.objects.filter(hidden=False).order_by('date').reverse()
    def get_messages(self):
        from post.models import NewsItem
        #return NewsItem.objects.filter(post__user_to__in=self.friends.all()).exclude(post__user=self).order_by('date').reverse()
        return NewsItem.objects.filter(user__in=self.friends.all()).exclude(post__user=self).order_by('date').reverse()

    @models.permalink
    def get_absolute_url(self):
        return ('profile.views.profile', [str(self.username)])

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)
    



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        up = UserProfile(user_ptr_id=instance.pk)
        up.__dict__.update(instance.__dict__)
        up.save()
post_save.connect(create_user_profile, sender=User)
