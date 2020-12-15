import time
from django.core.management.base import BaseCommand
from constance import config

from ._excel_squalaetp import ExcelSqualaetp
from squalaetp.models import Xelon
from psa.models import Corvet
from utils.scraping import ScrapingCorvet
from utils.django.validators import xml_parser
from utils.django.models import defaults_dict
from utils.conf import XLS_SQUALAETP_FILE


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('vin', nargs="?", type=str)
        parser.add_argument(
            '--squalaetp',
            action='store_true',
            dest='squalaetp',
            help='Import Corvet data for Squalaetp',
        )

    def handle(self, *args, **options):
        # r'^VF[37]\w{14}$'
        if options['vin']:
            vin = options['vin']
            data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(vin)
            data = str(xml_parser(data))
            self.stdout.write(data)
        if options['squalaetp']:
            self.stdout.write("[IMPORT_CORVET] Waiting...")
            squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)
            xelon_list = list(squalaetp.sheet['numero_de_dossier'])
            xelons = Xelon.objects.filter(
                numero_de_dossier__in=xelon_list, vin__regex=r'^V((F[37])|(R[137]))\w{14}$',
                vin_error=False, corvet__isnull=True)
            self.stdout.write(f"[IMPORT_CORVET] Xelon number = {xelons.count()}")
            nb_file = self._import(xelons)
            self.stdout.write(self.style.SUCCESS(f"[IMPORT_CORVET] Import completed: NB_CORVET = {nb_file}"))
        else:
            self.stdout.write("[IMPORT_CORVET] Waiting...")
            xelons = Xelon.objects.filter(
                vin__regex=r'^V((F[37])|(R[137]))\w{14}$', vin_error=False, corvet__isnull=True).order_by('-id')
            self._import(xelons, limit=True)

    def _import(self, queryset, limit=False):
        nb_created = 0
        for query in queryset:
            start_time = time.time()
            data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(query.vin)
            row = xml_parser(data)
            if row and row.get('donnee_date_entree_montage'):
                defaults = defaults_dict(Corvet, row, "vin")
                obj, created = Corvet.objects.update_or_create(vin=row["vin"], defaults=defaults)
                if created:
                    nb_created += 1
                query.corvet = obj
                delay_time = time.time() - start_time
                self.stdout.write(
                    self.style.SUCCESS(f"{query.numero_de_dossier} - {query.vin} updated in {delay_time}"))
            else:
                query.vin_error = True
                delay_time = time.time() - start_time
                self.stdout.write(
                    self.style.ERROR(f"{query.numero_de_dossier} - {query.vin} error VIN in {delay_time}"))
            query.save()
            if limit and nb_created >= 10:
                break
        return nb_created
