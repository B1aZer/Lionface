from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create new users'

    def handle(self, *args, **options):
        max_user = User.objects.count() + 1
        for x in xrange(max_user,max_user+11):
            try:
                max_user = x
                username = 'admin%s' % max_user
                email = 'admin@admin%s.com' % max_user
                user = User.objects.create_user(username, email, 'admin')
                user.first_name = 'admin%s' % max_user
                user.save()
                user = user.userprofile
                # adding to love page
                from pages.models import Pages, Membership
                page = Pages.objects.get(id=23)
                import datetime
                from_date = datetime.date(2008, 6, 24)
                Membership.objects.create(user=user,page=page,type='IN',from_date=from_date)
                #page.users_loved.add(user)
                #page.loves += 1
                #page.save()
            except:
                self.stdout.write('Error on: %s:%s' % (username,email))
                continue
            self.stdout.write('Successfully created: %s:%s' % (username,email))

