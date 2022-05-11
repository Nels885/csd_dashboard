from io import StringIO
from sbadmin import celery_app
from django.core.management import call_command


@celery_app.task
def cmd_sendemail_all_task():
    call_command('sendemail', '--late_products', '--pending_products', '--vin_error', '--vin_corvet', '--reman')


@celery_app.task
def cmd_sendemail_task(*args):
    """
    task for sendemail command
    :param args: --late_products, --pending_products, --vin_error, --vin_corvet, --reman
    :return:
        --late_products: Send email for the late products
        --pending_products: Send email for the pending products
        --vin_error: Send email for the V.I.N. error
        --vin_corvet: Send email for the access problem of Corvet data
        --reman: Send email for the REMAN batches in progress
    """
    call_command('sendemail', *args)


@celery_app.task
def cmd_import_excel_task():
    call_command('importexcel')
    call_command('loadsparepart')
    call_command('importcorvet')


@celery_app.task()
def cmd_loadcontract_task(*args):
    out = StringIO()
    call_command("loadcontract", *args, stdout=out)
    return out.getvalue()
