from django.db import models
from account.models import *
from django.db.models.signals import post_save

# Create your models here.

class Messages(models.Model):
    user = models.ForeignKey(UserProfile)
    user_to = models.ForeignKey(UserProfile, related_name='message_to')
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    read = models.BooleanField(default=False)

    def mark_read(self):
        self.read = True
        self.save()

    def save(self, *args, **kwargs):
        send = False
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
        if (send):
            super(Messages, self).save(*args, **kwargs)
        return send
