import time
from django.core.management.base import BaseCommand
from django.db.models import Q

from ._excel_squalaetp import ExcelSqualaetp
from squalaetp.models import Xelon, Sivin
from psa.models import Corvet, CorvetProduct
from utils.scraping import ScrapingCorvet, ScrapingSivin
from utils.django.validators import xml_parser, xml_sivin_parser
from utils.django.models import defaults_dict
from utils.conf import XLS_SQUALAETP_FILE


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('vin', nargs="?", type=str)
        parser.add_argument(
            '-i',
            '--immat',
            dest='immat',
            help='Vehicle license plate',
        )
        parser.add_argument(
            '--squalaetp',
            action='store_true',
            dest='squalaetp',
            help='Import Corvet data for Squalaetp',
        )

    def handle(self, *args, **options):
        if options['vin']:
            vin = options['vin']
            scrap = ScrapingCorvet()
            data = scrap.result(vin)
            data = str(xml_parser(data))
            self.stdout.write(data)
            scrap.close()
        elif options['immat']:
            self._import_sivin(options['immat'])
            self.stdout.write(self.style.SUCCESS("[IMPORT_SIVIN] Import completed!"))
        elif options['squalaetp']:
            self.stdout.write("[IMPORT_CORVET] Waiting...")
            squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)
            xelon_list = squalaetp.xelon_number_list()
            xelons = Xelon.objects.filter(
                numero_de_dossier__in=xelon_list, vin__regex=r'^V((F[37])|(R[137]))\w{14}$',
                vin_error=False, corvet__isnull=True)
            self.stdout.write(f"[IMPORT_CORVET] Xelon number = {xelons.count()}")
            nb_file = self._import(xelons)
            self.stdout.write(self.style.SUCCESS(f"[IMPORT_CORVET] Import completed: NB_CORVET = {nb_file}"))
        else:
            self.stdout.write("[IMPORT_CORVET] Waiting...")
            xelons = Xelon.objects.filter(vin__regex=r'^V((F[37])|(R[137]))\w{14}$', vin_error=False).order_by('-id')
            xelons = xelons.filter(Q(corvet__isnull=True) | Q(corvet__prods__update=True))[:50]
            nb_file = self._import(xelons, limit=True)
            self.stdout.write(self.style.SUCCESS(f"[IMPORT_CORVET] Import completed: NB_CORVET = {nb_file}"))

    def _import(self, queryset, limit=False):
        nb_import = 0
        scrap = ScrapingCorvet()
        for query in queryset:
            start_time = time.time()
            for attempt in range(2):
                data = scrap.result(query.vin)
                row = xml_parser(data)
                if scrap.ERROR or "ERREUR COMMUNICATION SYSTEME CORVET" in data:
                    nb_import += 1
                    delay_time = time.time() - start_time
                    self.stdout.write(
                        self.style.ERROR(f"{query.numero_de_dossier} - {query.vin} error CORVET in {delay_time}"))
                    break
                elif row and row.get('donnee_date_entree_montage'):
                    defaults = defaults_dict(Corvet, row, "vin")
                    obj, created = Corvet.objects.update_or_create(vin=row["vin"], defaults=defaults)
                    obj.prods.update = False
                    obj.prods.save()
                    nb_import += 1
                    query.corvet = obj
                    delay_time = time.time() - start_time
                    self.stdout.write(
                        self.style.SUCCESS(f"{query.numero_de_dossier} - {query.vin} updated in {delay_time}"))
                    break
                if attempt:
                    query.vin_error = True
                    query.corvet = None
                    delay_time = time.time() - start_time
                    self.stdout.write(
                        self.style.ERROR(f"{query.numero_de_dossier} - {query.vin} error VIN in {delay_time}"))
            query.save()
            if limit and nb_import >= 200:
                break
        scrap.close()
        return nb_import

    def _import_sivin(self, immat):
        start_time = time.time()
        self.stdout.write("[IMPORT_SIVIN] Waiting...")
        sivin = ScrapingSivin()
        data = sivin.result(immat)
        sivin.close()
        delay_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"SIVIN Data {data['immat_siv']} updated in {delay_time}"))
        data = xml_sivin_parser(data)
        print(data)
        if Corvet.objects.filter(vin=data['codif_vin']):
            corvet = ScrapingCorvet()
            row = corvet.result(data['codif_vin'])
            corvet.close()
            row = xml_parser(row)
            if row and row.get('donnee_date_entree_montage'):
                def_corvet = defaults_dict(Corvet, row, "vin")
                Corvet.objects.update_or_create(vin=row["vin"], defaults=def_corvet)
                delay_time = time.time() - start_time
                self.stdout.write(self.style.SUCCESS(f"CORVET Data {row['vin']} updated in {delay_time}"))
        def_sivin = defaults_dict(Sivin, data, "immat_siv")
        Sivin.objects.update_or_create(immat_siv=data["immat_siv"], defaults=def_sivin)
        delay_time = time.time() - start_time
        self.stdout.write(str(data))
        return data
