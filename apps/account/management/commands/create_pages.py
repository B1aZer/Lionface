from django.core.management.base import BaseCommand
from pages.models import Pages, Membership
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create new pages'

    def handle(self, *args, **options):
        max_user = Pages.objects.count() + 1
        for x in xrange(max_user,max_user+11):
            try:
                max_user = x
                username = 'page%s' % max_user
                page = Pages.objects.create(name = username, username = username, user= User.objects.get(id=1).userprofile, type='NP')
                #page.users_loved.add(user)
                #page.loves += 1
                #page.save()
            except:
                self.stdout.write('Error on: %s' % (username))
                continue
            self.stdout.write('Successfully created: %s' % (username))

