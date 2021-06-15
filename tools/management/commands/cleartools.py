from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from tools.models import TagXelon, ThermalChamber, Suptech, BgaTime


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
        parser.add_argument(
            '--suptech',
            action='store_true',
            dest='suptech',
            help='Delete all data in Suptech table',
        )
        parser.add_argument(
            '--bga_time',
            action='store_true',
            dest='bga_time',
            help='Delete all data in BgaTime table',
        )

    def handle(self, *args, **options):
        tables = []
        if options['tag_xelon']:
            TagXelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [TagXelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            tables.append("TagXelon")

        if options['thermal_chamber']:
            ThermalChamber.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ThermalChamber, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            tables.append("ThermalChamber")

        if options['suptech']:
            Suptech.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Suptech, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            tables.append("Suptech")

        if options['bga_time']:
            BgaTime.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [BgaTime, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            tables.append("BgaTime")

        for table in tables:
            self.stdout.write(self.style.SUCCESS(f"Suppression des données de la table {table} terminée!"))
