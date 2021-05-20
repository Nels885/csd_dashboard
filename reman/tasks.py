from sbadmin import celery_app
from django.core.management import call_command


@celery_app.task(bind=True)
def cmd_exportreman_task(self, *args):
    call_command("exportreman", *args)
