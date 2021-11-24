import re
import time
from sbadmin import celery_app

from utils.scraping import ScrapingCorvet
from utils.django.models import defaults_dict
from utils.django.validators import xml_parser
from .models import Corvet


@celery_app.task
def save_corvet_to_models(vin):
    msg = "Not VIN PSA"
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
        scrap.close()
    print(msg)
    return msg
