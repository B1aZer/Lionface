from celery.task import Task
from celery.registry import tasks
from django.core import management

class DeleteInactiveUsers(Task):
    def run(self, **kwargs):
        management.call_command('cleanupregistration', verbosity=0, interactive=False)
tasks.register(DeleteInactiveUsers)


