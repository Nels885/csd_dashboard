from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from psa.models import Multimedia, Ecu


class Command(BaseCommand):
    help = 'Clear Squalaetp tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--multimedia',
            action='store_true',
            dest='multimedia',
            help='Clear Multimedia table',
        )
        parser.add_argument(
            '--ecu',
            action='store_true',
            dest='ecu',
            help='Clear Ecu table',
        )

    def handle(self, *args, **options):

        if options['multimedia']:
            Multimedia.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Multimedia, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Multimedia terminée!"))
        if options['ecu']:
            Ecu.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Ecu, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Ecu terminée!"))
