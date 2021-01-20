from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from tools.models import TagXelon, ThermalChamber


class Command(BaseCommand):
    help = 'Clear Tools tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tag_xelon',
            action='store_true',
            dest='tag_xelon',
            help='Clear TagXelon table',
        )
        parser.add_argument(
            '--thermal_chamber',
            action='store_true',
            dest='thermal_chamber',
            help='Clear ThermalChamber table',
        )

    def handle(self, *args, **options):
        if options['tag_xelon']:
            TagXelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [TagXelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["TagXelon"]:
                self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))

        if options['thermal_chamber']:
            ThermalChamber.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ThermalChamber, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["ThermalChamber"]:
                self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))
