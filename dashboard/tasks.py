import os
from django.utils import timezone
from django.core.management.base import CommandError

from io import StringIO
from sbadmin import celery_app
from django.core.management import call_command

from utils.conf import CSD_ROOT


@celery_app.task
def cmd_sendemail_all_task():
    call_command('sendemail', '--late_products', '--pending_products', '--vin_error', '--vin_corvet', '--reman')
    return {"msg": "Envoi des Emails du matin terminés !"}


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
    return {"msg": "Envoi des Emails produits en cours terminés !"}


@celery_app.task
def cmd_import_excel_task():
    data = {}
    out = StringIO()
    call_command('importexcel', stdout=out)
    data['importexcel'] = out.getvalue()
    call_command('loadsparepart', stdout=out)
    data['loadsparepart'] = out.getvalue()
    call_command('importcorvet', '--all', stdout=out)
    data['importcorvet'] = out.getvalue()
    return data


@celery_app.task()
def cmd_loadcontract_task(*args):
    out = StringIO()
    call_command("loadcontract", *args, stdout=out)
    return out.getvalue()


@celery_app.task()
def cmd_database_backup_task(**kwargs):
    now = timezone.datetime.strftime(timezone.localtime(), "%d-%m-%Y")
    base_dir = kwargs.get("base_dir", os.path.join(CSD_ROOT, "TEMP"))
    try:
        base_dir = os.path.abspath(os.path.expanduser(base_dir[0]) + base_dir[1:])
        call_command("dumpdata", "-o", os.path.join(base_dir, f"dump_csd-dashboard-all_{now}.json"))
    except CommandError as err:
        return {"msg": f"CommandError: {err}"}
    return {"msg": "Backup database success!"}
