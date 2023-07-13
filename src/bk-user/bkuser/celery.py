import os

from celery import Celery
from kombu import Exchange, Queue

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bkuser.settings')

app = Celery('bkuser')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# set queue ha policy if use rabbitmq
# default queue name is bkuser
app.conf.task_queues = [
    Queue("bkuser", Exchange("bkuser"), routing_key="bkuser", queue_arguments={"x-ha-policy": "all"}),
]
