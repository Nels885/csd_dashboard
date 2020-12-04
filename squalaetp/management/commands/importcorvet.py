import time
from django.core.management.base import BaseCommand
from constance import config

from squalaetp.models import Xelon
from psa.models import Corvet
from utils.scraping import ScrapingCorvet
from utils.django.validators import xml_parser
from utils.django.models import defaults_dict


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('vin', nargs="?", type=str)

    def handle(self, *args, **options):
        if options['vin']:
            vin = options['vin']
            data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(vin)
            data = str(xml_parser(data))
            self.stdout.write(data)
        else:
            xelons = Xelon.objects.filter(
                vin__regex=r'^VF[37]\w{14}$', date_retour__isnull=False, corvet__isnull=True).order_by('-date_retour')
            for xelon in xelons[:10]:
                start_time = time.time()
                data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(xelon.vin)
                row = xml_parser(data)
                if row.get('donnee_date_entree_montage'):
                    defaults = defaults_dict(Corvet, row, "vin")
                    obj, created = Corvet.objects.update_or_create(vin=row["vin"], defaults=defaults)
                    xelon.corvet = obj
                    xelon.save()
                    delay_time = time.time() - start_time
                    self.stdout.write(
                        self.style.SUCCESS(f"{xelon.numero_de_dossier} - {xelon.vin} updated in {delay_time}"))
                else:
                    delay_time = time.time() - start_time
                    self.stdout.write(
                        self.style.ERROR(f"{xelon.numero_de_dossier} - {xelon.vin} error VIN in {delay_time}"))
