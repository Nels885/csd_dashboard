import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError

from squalaetp.models import ProductCode, SparePart
from psa.models import Ecu, Multimedia
from utils.conf import get_path

from ._csv_extraction import CsvSparePart

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Stock table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import CSV file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SPAREPART] Waiting...")

        if options['filename'] is not None:
            extraction = CsvSparePart(options['filename'])
        else:
            extraction = CsvSparePart(get_path('CSV_EXTRACTION_FILE'))

        nb_part_before = ProductCode.objects.count()
        nb_part_update = 0
        SparePart.objects.exclude(cumul_dispo=0).update(cumul_dispo=0)
        if not extraction.ERROR:
            for row in extraction.read():
                logger.info(row)
                code_magasin = row.pop("code_magasin")
                code_produit = row.pop("code_produit")
                code_zone = row.pop("code_zone")
                code_emplacement = row.pop("code_emplacement")
                try:
                    part_obj, part_created = ProductCode.objects.get_or_create(name=code_produit)
                    obj, created = SparePart.objects.update_or_create(
                        code_magasin=code_magasin, code_zone=code_zone,
                        code_emplacement=code_emplacement, code_produit=part_obj, defaults=row
                    )
                    if not created:
                        nb_part_update += 1
                except IntegrityError as err:
                    logger.error(f"[SPAREPART_CMD] IntegrityError: {code_produit} - {err}")
                except ProductCode.MultipleObjectsReturned as err:
                    logger.error(f"[PRODUCTCODE_CMD] MultipleObjectsReturned: {code_produit} - {err}")
                except SparePart.MultipleObjectsReturned as err:
                    logger.error(f"[SPAREPART_CMD] MultipleObjectsReturned: {code_produit} - {err}")
                except DataError as err:
                    logger.error(f"[SPAREPART_CMD] DataError: {code_produit} - {err}")
            self._relation_update()
            nb_part_after = ProductCode.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[SPAREPART] Data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_part_after - nb_part_before, nb_part_update, nb_part_after
                    )
                )
            )
        else:
            self.stdout.write(f"[SPAREPART_FILE] {extraction.ERROR}")

    def _relation_update(self):
        self.stdout.write("[PRODUCTCODE] Waiting...")
        for ecu in Ecu.objects.all():
            if ecu.relation_by_name and len(ecu.xelon_name) > 0:
                for prod in ProductCode.objects.filter(name__icontains=str(ecu.xelon_name)):
                    prod.ecus.add(ecu)
                ecu.relation_by_name = False
                ecu.save()
            if ecu.label_ref:
                for prod in ProductCode.objects.filter(name__contains=str(ecu.label_ref)[:-2]):
                    prod.ecus.add(ecu)
            elif ecu.comp_ref:
                for prod in ProductCode.objects.filter(name__contains=str(ecu.comp_ref)[:-2]):
                    prod.ecus.add(ecu)
        for media in Multimedia.objects.all():
            if media.label_ref:
                for prod in ProductCode.objects.filter(name__contains=str(media.label_ref)[:-2]):
                    prod.medias.add(media)
            elif media.comp_ref:
                for prod in ProductCode.objects.filter(name__contains=str(media.comp_ref)[:-2]):
                    prod.medias.add(media)
        self.stdout.write(self.style.SUCCESS("[PRODUCTCODE] Data update completed!"))
