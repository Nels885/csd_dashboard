from sbadmin import celery_app
from django.core.management import call_command
from django.core.mail import EmailMessage


@celery_app.task(bind=True)
def cmd_suptech_task(self):
    call_command('suptech')


@celery_app.task(bind=True)
def send_email_task(self, subject, body, from_email, to, cc, files=None):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to, cc=cc)
    if files:
        for f in files:
            email.attach(f.name, f.read(), f.content_type)
    email.send()
