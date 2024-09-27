import datetime
import numpy as np
from io import StringIO
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
    out = StringIO()
    call_command('suptech', *args, stdout=out)
    return out.getvalue()


@celery_app.task
def cmd_infotech_task(*args):
    """
    Task for the Infotech command
        Interact with the Infotech table in the database
    :param args: --email or None
    :return:
        --email: Send email for Suptech in progress
        None: do nothing
    """
    out = StringIO()
    call_command('infotech', *args, stdout=out)
    return out.getvalue()


@celery_app.task(bind=True)
def send_email_task(self, subject, body, from_email, to, cc, files=None):
    email = EmailMessage(
        subject=subject, body=body, from_email=from_email, to=string_to_list(to), cc=string_to_list(cc)
    )
    if files:
        [email.attach_file(file) for file in files]
    email.send()


@celery_app.task
def suptech_days_late_task(*args, **kwargs):
    from .models import Suptech
    queryset = Suptech.objects.exclude(status__in=['Cloturée', 'Annulée'])
    queryset = queryset.filter(date__gte=datetime.date(2024, 1, 1))
    for query in queryset:
        if query.created_at:
            start_date = query.created_at.strftime("%Y-%m-%d")
            if query.modified_at:
                end_date = query.modified_at.strftime("%Y-%m-%d")
            else:
                end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            query.days_late = np.busday_count(start_date, end_date)
            query.save()
