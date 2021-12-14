import re
import time
from sbadmin import celery_app
from celery_progress.backend import ProgressRecorder

from utils.scraping import ScrapingCorvet
from utils.django.models import defaults_dict
from utils.django.validators import xml_parser
from .models import Corvet, CorvetOption


@celery_app.task
def save_corvet_to_models(vin):
    msg = f"{vin} Not VIN PSA"
    if re.match(r'^[VWZ][FLR0]\w{15}$', str(vin)):
        scrap = ScrapingCorvet()
        start_time = time.time()
        for attempt in range(2):
            row = xml_parser(scrap.result(vin))
            if scrap.ERROR or "ERREUR COMMUNICATION SYSTEME CORVET" in row:
                delay_time = time.time() - start_time
                msg = f"{vin} error CORVET in {delay_time}"
                break
            elif row and row.get('donnee_date_entree_montage'):
                defaults = defaults_dict(Corvet, row, "vin")
                obj, created = Corvet.objects.update_or_create(vin=row.get("vin"), defaults=defaults)
                obj.prods.update = False
                obj.prods.save()
                delay_time = time.time() - start_time
                msg = f"{vin} updated in {delay_time}"
                break
            if attempt:
                delay_time = time.time() - start_time
                msg = f"{vin} error VIN in {delay_time}"
                Corvet.objects.filter(vin=vin).delete()
        scrap.close()
    print(msg)
    return msg


@celery_app.task(bind=True)
def import_corvet_task(self, vin):
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(1, 4)
    msg = f"{vin} Not VIN PSA"
    if re.match(r'^[VWZ][FLR0]\w{15}$', str(vin)):
        scrap = ScrapingCorvet()
        progress_recorder.set_progress(2, 4)
        if scrap.ERROR:
            msg = f"{vin} error CORVET"
        else:
            msg = scrap.result(vin)
        progress_recorder.set_progress(3, 4)
        scrap.close()
    return msg


@celery_app.task(bind=True)
def import_corvet_list_task(self, *args):
    progress_recorder = ProgressRecorder(self)
    list_args, msg = args, ""
    CorvetOption.objects.update(filter="")
    for count, vin in enumerate(list_args):
        corvets = Corvet.objects.filter(vin=vin, prods__update=False)
        CorvetOption.objects.filter(corvet=vin).update(filter="ICARE")
        progress_recorder.set_progress(count, len(list_args))
        if not corvets:
            if re.match(r'^[VWZ][FLR0]\w{15}$', str(vin)):
                scrap = ScrapingCorvet()
                start_time = time.time()
                for attempt in range(2):
                    row = xml_parser(scrap.result(vin))
                    if scrap.ERROR or "ERREUR COMMUNICATION SYSTEME CORVET" in row:
                        delay_time = time.time() - start_time
                        msg += f"{vin} error CORVET in {delay_time}"
                        break
                    elif row and row.get('donnee_date_entree_montage'):
                        defaults = defaults_dict(Corvet, row, "vin")
                        obj, created = Corvet.objects.update_or_create(vin=row.get("vin"), defaults=defaults)
                        obj.prods.update = False
                        obj.prods.save()
                        delay_time = time.time() - start_time
                        msg += f"{vin} updated in {delay_time}"
                        break
                    if attempt:
                        delay_time = time.time() - start_time
                        msg += f"{vin} error VIN in {delay_time}"
                        Corvet.objects.filter(vin=vin).delete()
                scrap.close()
            else:
                msg += f"{vin} Not VIN PSA"
        else:
            msg += f"{vin} data OK"
        msg += "\r\n"
    return msg
