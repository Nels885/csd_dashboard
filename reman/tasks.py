from sbadmin import celery_app
from django.core.management import call_command


@celery_app.task
def cmd_exportreman_task(*args):
    """
    task for exportreman command
        Export CSV file for Batch REMAN
    :param args: --batch, --repair, --cal_ecu, --check_out, --scan_in_out
    :return:
        --batch: Export all batch
        --repair: Export repair in progress
        --cal_ecu: Export CAL ECU
        --check_out: Export REMAN REFERENCE for Check Out repair
        --scan_in_out: Export REMAN REFERENCE for Scan IN/OUT
    """
    call_command("exportreman", *args)
