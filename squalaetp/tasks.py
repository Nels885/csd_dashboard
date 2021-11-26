import time
from io import StringIO
from sbadmin import celery_app
from django.core.management import call_command
from django.core.mail import EmailMessage

from utils.scraping import ScrapingSivin, ScrapingCorvet
from utils.django.models import defaults_dict
from utils.django.validators import xml_sivin_parser, xml_parser
from .models import Sivin
from psa.models import Corvet


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


@celery_app.task()
def cmd_importcorvet_task(*args):
    print("cmd_importcorvet_tash in progress...")
    print(f"cmd : importcorvet {' '.join(args)}")
    out = StringIO()
    call_command("importcorvet", f"{' '.join(args)}", stdout=out)
    return out.getvalue()


@celery_app.task(bind=True)
def send_email_task(self, subject, body, from_email, to, cc, files=None):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to, cc=cc)
    if files:
        for f in files:
            email.attach(f.name, f.read(), f.content_type)
    email.send()


@celery_app.task
def save_sivin_to_models(immat):
    msg = "SIVIN not Found"
    start_time = time.time()
    sivin = ScrapingSivin()
    data = xml_sivin_parser(sivin.result(immat))
    sivin.close()
    if sivin.ERROR or "ERREUR COMMUNICATION SYSTEME SIVIN" in data:
        delay_time = time.time() - start_time
        msg = f"{immat} - error SIVIN in {delay_time}"
    elif data and data.get('immat_siv'):
        delay_time = time.time() - start_time
        msg = f"SIVIN Data {data.get('immat_siv')} updated in {delay_time}"
        if not Corvet.objects.filter(vin=data.get('codif_vin')):
            corvet = ScrapingCorvet()
            row = xml_parser(corvet.result(data.get('codif_vin')))
            corvet.close()
            if row and row.get('donnee_date_entree_montage'):
                def_corvet = defaults_dict(Corvet, row, "vin")
                Corvet.objects.update_or_create(vin=row["vin"], defaults=def_corvet)
                delay_time = time.time() - start_time
                msg += f"\r\nCORVET Data {row.get('vin')} updated in {delay_time}"
        def_sivin = defaults_dict(Sivin, data, "immat_siv")
        Sivin.objects.update_or_create(immat_siv=data.get("immat_siv"), defaults=def_sivin)
    else:
        delay_time = time.time() - start_time
        msg = f"{immat} - not data SIVIN in {delay_time}"
    print(msg)
    return msg
