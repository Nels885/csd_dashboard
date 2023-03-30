import time
from sbadmin import celery_app
from celery_progress.backend import ProgressRecorder

from utils.scraping import ScrapingCorvet, xml_parser
from utils.django.models import defaults_dict
from .models import Corvet, CorvetOption

from utils.django.validators import vin_psa_isvalid


@celery_app.task
def save_corvet_to_models(vin, **kwargs):
    msg = f"{vin} Not VIN PSA"
    if vin_psa_isvalid(vin):
        scrap = ScrapingCorvet(test=kwargs.get("test", False))
        start_time = time.time()
        for attempt in range(2):
            row = xml_parser(scrap.result(vin))
            if scrap.ERROR or "ERREUR COMMUNICATION SYSTEME CORVET" in row:
                delay_time = time.time() - start_time
                msg = f"{vin} error CORVET in {delay_time}"
                break
            elif isinstance(row, dict) and row.get('donnee_date_entree_montage'):
                defaults = defaults_dict(Corvet, row, "vin")
                obj, created = Corvet.objects.update_or_create(vin=row.get("vin"), defaults=defaults)
                obj.opts.update = False
                obj.opts.save()
                delay_time = time.time() - start_time
                msg = f"{vin} updated in {delay_time}"
                break
            if attempt:
                Corvet.objects.filter(vin=vin).delete()
                delay_time = time.time() - start_time
                msg = f"{vin} error VIN in {delay_time}"
        scrap.quit()
    return msg


@celery_app.task(bind=True)
def import_corvet_task(self, vin):
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(1, 4)
    msg = f"{vin} Not VIN PSA"
    if vin_psa_isvalid(vin):
        scrap = ScrapingCorvet()
        progress_recorder.set_progress(2, 4)
        if scrap.ERROR:
            msg = f"{vin} error CORVET"
        else:
            msg = scrap.result(vin)
        progress_recorder.set_progress(3, 4)
        scrap.quit()
    return msg


@celery_app.task(bind=True)
def import_corvet_list_task(self, *args, **kwargs):
    progress_recorder = ProgressRecorder(self)
    list_args, msg = args, ""
    for count, vin in enumerate(list_args):
        corvets = Corvet.objects.filter(vin=vin, opts__update=False)
        if kwargs.get('corvet_tag'):
            CorvetOption.objects.filter(corvet=vin).update(tag=kwargs.get('corvet_tag'))
        progress_recorder.set_progress(count, len(list_args))
        if not corvets:
            if vin_psa_isvalid(vin):
                scrap = ScrapingCorvet()
                start_time = time.time()
                for attempt in range(2):
                    row = xml_parser(scrap.result(vin))
                    if scrap.ERROR or "ERREUR COMMUNICATION SYSTEME CORVET" in row:
                        delay_time = time.time() - start_time
                        msg += f"{vin} error CORVET in {delay_time}"
                        break
                    elif isinstance(row, dict) and row.get('donnee_date_entree_montage'):
                        defaults = defaults_dict(Corvet, row, "vin")
                        obj, created = Corvet.objects.update_or_create(vin=row.get("vin"), defaults=defaults)
                        obj.opts.tag = "ICARE"
                        obj.opts.update = False
                        obj.opts.save()
                        delay_time = time.time() - start_time
                        msg += f"{vin} updated in {delay_time}"
                        break
                    elif attempt:
                        delay_time = time.time() - start_time
                        msg += f"{vin} error VIN in {delay_time}"
                        Corvet.objects.filter(vin=vin).delete()
                scrap.quit()
            else:
                msg += f"{vin} Not VIN PSA"
        else:
            msg += f"{vin} data OK"
        msg += "\r\n"
    return {
        "detail": "Successfully import VIN PSA",
        "message": msg
    }
