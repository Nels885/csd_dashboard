import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError

from psa.models import CanRemote

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT

from ._csv_file import CsvCanRemote

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Export CSV file for Batch REMAN'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--filename',
            dest='filename',
            help='Specify import canremote csv file',
        )
        parser.add_argument(
            '--export_remote',
            action='store_true',
            dest='export_remote',
            help='Export all CanRemote data',
        )
        parser.add_argument(
            '--import_remote',
            action='store_true',
            dest='import_remote',
            help='Export all CanRemote data',
        )

    def handle(self, *args, **options):
        if options['export_remote']:
            self.stdout.write("[CANREMOTE_EXPORT] Waiting...")

            filename = "canremote.csv"
            path = os.path.join(CSD_ROOT, "EXTS")
            header = [f.name for f in CanRemote._meta.local_fields if f.name != "id"]
            queryset = CanRemote.objects.all().order_by('type', 'location', 'product', 'vehicle')
            values_list = queryset.values_list(*header).distinct()
            try:
                ExportExcel(values_list=values_list, filename=filename, header=header).file(path, False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "[CANREMOTE_EXPORT] Export completed: NB_BATCH = {} | FILE = {}".format(
                            queryset.count(), os.path.join(path, filename)
                        )
                    )
                )
            except FileNotFoundError as err:
                self.stdout.write(self.style.ERROR("[CANREMOTE_EXPORT] {}".format(err)))
                logger.error(f"FileNotFoundError: {err}")
        if options['import_remote'] and options['filename']:
            self.stdout.write("[CANREMOTE_IMPORT] Waiting...")
            excel = CsvCanRemote(options['filename'])
            nb_before = CanRemote.objects.count()
            nb_update = 0
            if not excel.ERROR:
                for row in excel.read():
                    print(row)
                    logger.info(row)
                    label = row.pop("label")
                    type = row.pop("type")
                    product = row.pop("product")
                    vehicle = row.pop("vehicle")
                    row_name = f"{label}_{type}_{product}{vehicle}"
                    try:
                        obj, created = CanRemote.objects.update_or_create(
                            label=label, type=type, product=product, vehicle=vehicle, defaults=row
                        )
                        if not created:
                            nb_update += 1
                    except IntegrityError as err:
                        logger.error(f"[SPAREPART_CMD] IntegrityError: {row_name} - {err}")
                    except CanRemote.MultipleObjectsReturned as err:
                        logger.error(f"[PRODUCTCODE_CMD] MultipleObjectsReturned: {row_name} - {err}")
                    except DataError as err:
                        logger.error(f"[SPAREPART_CMD] DataError: {row_name} - {err}")
                nb_part_after = CanRemote.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        "[CANREMOTE] Data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                            excel.nrows, nb_part_after - nb_before, nb_update, nb_part_after
                        )
                    )
                )
            else:
                self.stdout.write(f"[SPAREPART_FILE] {excel.ERROR}")
