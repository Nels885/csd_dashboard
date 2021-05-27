from sbadmin import celery_app
from django.core.management import call_command


@celery_app.task
def cmd_sendemail_all_task():
    call_command('sendemail', '--late_products', '--vin_error', '--vin_corvet', '--reman')


@celery_app.task
def cmd_import_excel_task():
    call_command('importexcel')
    call_command('loadsparepart')
    call_command('importcorvet')
