from celery.task import Task
from celery.registry import tasks
from django.core import management

class UpdateSearchIndex(Task):
    def run(self, **kwargs):
        management.call_command('update_index', verbosity=0, interactive=False)
tasks.register(UpdateSearchIndex)