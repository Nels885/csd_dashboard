from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from squalaetp.models import Xelon, Indicator, ProductCategory


class Command(BaseCommand):
    help = 'Clear Squalaetp tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xelon',
            action='store_true',
            dest='xelon',
            help='Clear Xelon table',
        )
        parser.add_argument(
            '--indicator',
            action='store_true',
            dest='indicator',
            help='Clear Indicator table',
        )
        parser.add_argument(
            '--prod_category',
            action='store_true',
            dest='prod_category',
            help='Clear ProductCategory table',
        )

    def handle(self, *args, **options):

        if options['xelon']:
            Xelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Xelon terminée!"))
        if options['indicator']:
            Indicator.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Indicator, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Indicator terminée!"))
        if options['prod_category']:
            ProductCategory.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ProductCategory, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table ProductCategory terminée!"))
