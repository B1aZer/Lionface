from django.core.management.base import BaseCommand
from account.models import Degree

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for d in Degree.objects.all():
            d.delete()

        self.stdout.write('Successfully deleted')

