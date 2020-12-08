from django.core.management.base import BaseCommand

from psa.models import Corvet

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT, conf


class Command(BaseCommand):
    help = 'Export CSV file for Batch REMAN'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corvet',
            action='store_true',
            dest='corvet',
            help='Export all corvet',
        )

    def handle(self, *args, **options):
        if options['corvet']:
            self.stdout.write("[CORVET] Waiting...")

            filename = "squalaetp_corvet"
            path = os.path.join(CSD_ROOT, conf.EXPORT_PATH)
            header = [f.name for f in Corvet._meta.local_fields]
            queryset = Corvet.objects.exclude(donnee_date_entree_montage__isnull=True)
            values_list = None
            ExportExcel(queryset=queryset, filename=filename, header=header, values_list=values_list).file(path, False)
            self.stdout.write(
                self.style.SUCCESS(
                    "[BATCH] Export completed: NB_BATCH = {} | FILE = {}.csv".format(
                        queryset.count(), os.path.join(path, filename)
                    )
                )
            )
