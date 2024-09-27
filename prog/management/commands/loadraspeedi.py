import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError

from prog.models import Raspeedi
from psa.models import Multimedia
from utils.conf import get_path
from utils.django.models import defaults_dict

from ._excel_raspeedi import ExcelRaspeedi

# Get an instance of a logger
logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Raspeedi table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[RASPEEDI] Waiting...")

        if options['filename'] is not None:
            path_file = options['filename']
            excel = ExcelRaspeedi(path_file)
        else:
            path_file = get_path('XLS_RASPEEDI_FILE')
            excel = ExcelRaspeedi(path_file)
        nb_before = Raspeedi.objects.count()
        nb_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                ref_boitier = row.pop("ref_boitier")
                try:
                    rasp_values = defaults_dict(Raspeedi, row)
                    obj, created = Raspeedi.objects.update_or_create(ref_boitier=ref_boitier, defaults=rasp_values)
                    if not created:
                        nb_update += 1
                    values = {
                        "name": row.get("produit", ""), "level": row.get("facade", ""),
                        "oe_reference": row.get("ref_mm", ""),
                    }
                    values.update(defaults_dict(Multimedia, row))
                    Multimedia.objects.update_or_create(comp_ref=ref_boitier, defaults=values)
                except IntegrityError as err:
                    logger.error(
                        f"[RASPEEDI_CMD] IntegrityError: {ref_boitier} - {err} of file : '{path_file}'"
                    )
                except DataError as err:
                    logger.error(
                        f"[RASPEEDI_CMD] DataError: {ref_boitier} - {err} of file : '{path_file}'")
            nb_after = Raspeedi.objects.count()
            self.stdout.write(f"[RASPEEDI_FILE] '{path_file}' => OK")
            self.stdout.write(
                self.style.SUCCESS(
                    f"[RASPEEDI_CMD] data update completed: EXCEL_LINES = {excel.nrows} | " +
                    f"ADD = {nb_after - nb_before} | UPDATE = {nb_update} | TOTAL = {nb_after}"
                )
            )
        else:
            self.stdout.write(f"[RASPEEDI_FILE] {excel.ERROR}")
