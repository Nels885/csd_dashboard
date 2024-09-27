import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError

from prog.models import Programing
from psa.models import Multimedia
from utils.conf import get_path
from utils.django.models import defaults_dict

from ._excel_raspeedi import ExcelPrograming

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Programing table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[PROGRAMING] Waiting ...")

        if options['filename'] is not None:
            path_file = options['filename']
            excel = ExcelPrograming(path_file)
        else:
            path_file = get_path('XLS_RASPEEDI_FILE')
            excel = ExcelPrograming(path_file)
        self._programing(excel)

    def _programing(self, excel):
        nb_before = Programing.objects.count()
        nb_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                psa_barcode = row.pop("psa_barcode")
                try:
                    multimedia = Multimedia.objects.filter(comp_ref=psa_barcode).first()
                    values = {'multimedia': multimedia}
                    values.update(defaults_dict(Programing, row))
                    obj, created = Programing.objects.update_or_create(psa_barcode=psa_barcode, defaults=values)
                    if not created:
                        nb_update += 1
                except IntegrityError as err:
                    logger.error(f"[PROGRAMING_CMD] IntegrityError: {psa_barcode} - {err}")
                except DataError as err:
                    logger.error(f"[PROGRAMING_CMD] DataError: {psa_barcode} - {err}")
            nb_after = Programing.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"[PROGRAMING] data update completed: EXCEL_LINES = {excel.nrows} | " +
                    f"ADD = {nb_after - nb_before} | UPDATE = {nb_update} | TOTAL = {nb_after}"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f"[PROGRAMING_CMD] {excel.ERROR}"))
