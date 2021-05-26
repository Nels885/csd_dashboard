import os
from django.core.management import call_command

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbadmin.settings.production')

app = Celery('sbadmin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task
def send_email_task():
    call_command('sendemail', '--late_products', '--vin_error', '--vin_corvet', '--reman')


@app.task
def import_excel_task():
    call_command('importexcel')
    call_command('loadsparepart')
    call_command('importcorvet')


@app.task
def export_reman_task():
    call_command('exportreman', '--batch', '--repair', '--check_out', '--cal_ecu')


@app.task
def suptech_task():
    call_command('suptech')
