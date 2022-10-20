import os
import subprocess

from celery import Celery
from celery.signals import setup_logging
from celery.exceptions import TaskError

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbadmin.settings.development')

app = Celery('sbadmin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task()
def subprocess_task(*args):
    """
    :param args:
        The different arguments of the shell command for linux
        example:
            ("rsync", "-avr", "<SOURCE>" "<DIR>")
    :return:
        Information dictionary or error message if not args
    """
    args_list = list(args)
    if args_list:
        p = subprocess.Popen(args_list, stdout=subprocess.PIPE, shell=False, encoding="utf-8")
        p.wait()
        out, err = p.communicate()
        return {"cmd": " ".join(args_list), "out": out, "err": err}
    raise TaskError('Arguments not found !')
