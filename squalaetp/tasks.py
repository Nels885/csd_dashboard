import time
from io import StringIO
from sbadmin import celery_app
from django.core.management import call_command
from django.core.mail import EmailMessage

from utils.scraping import ScrapingSivin, ScrapingCorvet, xml_sivin_parser, xml_parser
from utils.django.models import defaults_dict
from utils.django.validators import vin_psa_isvalid
from .models import Sivin
from psa.models import Corvet


@celery_app.task
def cmd_loadsqualaetp_task(*args):
    print("cmd_loadsqualaetp_task in progress...")
    print(f"cmd : importexcel {' '.join(args)}")
    out = StringIO()
    call_command("importexcel", *args, stdout=out)
    if "--tests" in args:
        return {"msg": "Importation Squalaetp terminée avec rapport de test."}
    elif "email Erreur" in out.getvalue():
        return {"msg": "Erreur d'importation Squalaetp, voir l'email du rapport !!", "tags": "warning"}
    return {"msg": "Importation Squalaetp terminée."}


@celery_app.task
def cmd_exportsqualaetp_task():
    print("cmd_exportsqualaetp_task in progress...")
    out = StringIO()
    call_command("exportsqualaetp", stdout=out)
    print(out.getvalue())
    if "Export error" in out.getvalue():
        return {"msg": "Erreur d'exportation Squalaetp, fichier en lecture seule !!", "tags": "warning"}
    return {"msg": "Exportation Squalaetp terminée.", "tags": "success"}


@celery_app.task
def cmd_importcorvet_task(*args):
    print("cmd_importcorvet_task in progress...")
    print(f"cmd : importcorvet {' '.join(args)}")
    out = StringIO()
    call_command("importcorvet", *args, stdout=out)
    return out.getvalue()


@celery_app.task(bind=True)
def send_email_task(self, subject: str, body: str, from_email: str, to: list, cc: list, files=None):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to, cc=cc)
    if files:
        for f in files:
            email.attach(f.name, f.read(), f.content_type)
    email.send()
    return {"msg": "Envoi email terminé.", "subject": subject, "from_email": from_email, "to": to}


@celery_app.task
def save_sivin_to_models(immat, **kwargs):
    msg = "SIVIN not Found"
    if not immat.isnumeric() and (6 < len(immat) < 11):
        start_time = time.time()
        sivin = ScrapingSivin(test=kwargs.get("test", False))
        data = xml_sivin_parser(sivin.result(immat))
        sivin.quit()
        if sivin.ERROR or "ERREUR COMMUNICATION SYSTEME SIVIN" in data:
            delay_time = time.time() - start_time
            msg = f"{immat} - error SIVIN in {delay_time}"
        elif isinstance(data, dict) and data.get('immat_siv'):
            delay_time = time.time() - start_time
            msg = f"SIVIN Data {data.get('immat_siv')} updated in {delay_time}"
            vin = data.get('codif_vin')
            if vin_psa_isvalid(vin) and not Corvet.objects.filter(vin=vin):
                corvet = ScrapingCorvet()
                row = xml_parser(corvet.result(data.get('codif_vin')))
                corvet.quit()
                if isinstance(row, dict) and row.get('donnee_date_entree_montage'):
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
