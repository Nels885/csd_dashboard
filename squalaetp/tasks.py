from io import StringIO
from sbadmin import celery_app
from django.core.management import call_command
from django.core.mail import EmailMessage


@celery_app.task
def cmd_loadsqualaetp_task():
    out = StringIO()
    call_command("loadsqualaetp", "--xelon_update", stdout=out)
    return {"msg": "Importation Squalaetp terminée."}


@celery_app.task
def cmd_exportsqualaetp_task():
    out = StringIO()
    call_command("exportsqualaetp", stdout=out)
    if "Export error" in out.getvalue():
        return {"msg": out.getvalue()}
    return {"msg": "Exportation Squalaetp terminée."}


@celery_app.task(bind=True)
def send_email_task(self, subject, body, from_email, to, cc, files=None):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to, cc=cc)
    if files:
        for f in files:
            email.attach(f.name, f.read(), f.content_type)
    email.send()
