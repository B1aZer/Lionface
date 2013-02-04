from django.db import models
from account.models import *
from django.db.models.signals import post_save

# Create your models here.

class Messaging(models.Model):
    user = models.ForeignKey(UserProfile)
    user_to = models.ForeignKey(UserProfile, related_name='message_to')
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    read = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    in_chat = models.BooleanField(default=False)

    def mark_read(self):
        self.read = True
        self.viewed = True
        self.save()

    def mark_viewed(self):
        self.viewed = True
        self.save()

    def save(self, *args, **kwargs):
        send = self.user_to.check_messages(self.user)
        """
        #checking settings
        if self.user_to.check_option('send_message',"Public"):
            send = True
        elif self.user_to.check_option('send_message',"Friends"):
            if self.user_to.has_friend(self.user):
                send = True
        elif self.user_to.check_option('send_message',"Friend's Friends"):
            if self.user_to.has_friends_friend(self.user):
                send = True
        elif self.user_to.check_option('send_message',"Off"):
            pass
        else:
            send = True
        # Blocked Users
        #if self.user in self.user_to.get_blocked():
            #send = False
        # if user has previous messages from this user
        sent = Messaging.objects.filter(user=self.user_to, user_to=self.user).count()
        if not send:
            if sent:
                send = True
        """
        if (send):
            super(Messaging, self).save(*args, **kwargs)
        return send
