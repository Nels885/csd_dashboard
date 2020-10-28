from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.utils import timezone
from django.db import connection

from squalaetp.models import Indicator

from utils.data.analysis import ProductAnalysis


class Command(BaseCommand):
    help = 'Interact with the Xelon table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Xelon table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[INDICATOR] Waiting...")

        if options['delete']:
            Indicator.objects.all().delete()
            Indicator.xelons.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Indicator, Indicator.xelons.through, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Indicator"]:
                self.stdout.write(self.style.WARNING("Suppression des données de la table {} terminée!".format(table)))
        else:
            prod = ProductAnalysis()
            defaults = {
                "products_to_repair": prod.pending,
                "express_products": prod.express,
                "late_products": prod.late,
                "output_products": 0,
            }
            obj, created = Indicator.objects.update_or_create(date=timezone.now(), defaults=defaults)
            for query in prod.pendingQueryset:
                obj.xelons.add(query)
            self.stdout.write(self.style.SUCCESS("[INDICATOR] data update completed"))
