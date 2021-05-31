from sbadmin import celery_app
from django.core.management import call_command
from django.core.mail import EmailMessage

from utils.conf import string_to_list


@celery_app.task
def cmd_suptech_task(*args):
    """
    Task for the Suptech command
        Interact with the Suptech table in the database
    :param args: --email, --first or None
    :return:
        --email: Send email for Suptech in progress
        --first: Adding first data in Suptech table
        None: Import data from CSV file to Suptech table and export data to XLS file
    """
    call_command('suptech', *args)


@celery_app.task(bind=True)
def send_email_task(self, subject, body, from_email, to, cc, files=None):
    email = EmailMessage(
        subject=subject, body=body, from_email=from_email, to=string_to_list(to), cc=string_to_list(cc)
    )
    if files:
        for f in files:
            email.attach(f.name, f.read(), f.content_type)
    email.send()
