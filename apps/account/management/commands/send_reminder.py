from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
import datetime as dateclass
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Send reminder to inactive users'

    def handle(self, *args, **options):
        now = timezone.now()
        last_week = now - dateclass.timedelta(days=7)
        inactive_users = User.objects.filter(last_login__lt=last_week)
        for user in inactive_users:
            userprofile = user.userprofile
            if userprofile.last_seen() < last_week:
                new_mess = userprofile.new_messages_count()
                new_notf = userprofile.new_notifcations()
                site = Site.objects.get_current()
                if not new_mess and not new_notf:
                    ctx_dict = {'user': userprofile,
                            'site': site}
                    subject = render_to_string('reminder/reminder_email_subject_nonews.txt',
                                   ctx_dict)
                    subject = ''.join(subject.splitlines())
                    message = render_to_string('reminder/reminder_email_nonews.txt',
                                   ctx_dict)
                else:
                    ctx_dict = {'user': userprofile,
                            'messages_count':new_mess,
                            'notifications_count':new_notf,
                            'site': site}
                    subject = render_to_string('reminder/reminder_email_subject.txt',
                                   ctx_dict)
                    subject = ''.join(subject.splitlines())
                    message = render_to_string('reminder/reminder_email.txt',
                                   ctx_dict)
                user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
                    #self.stdout.write('%s was last seen long ago %s' % (userprofile.username, userprofile.last_seen()))


