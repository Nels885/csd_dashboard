from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from psa.models import Multimedia, Ecu, Corvet


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
        parser.add_argument(
            '--corvet',
            action='store_true',
            dest='corvet',
            help='Delete all data in Corvet table',
        )

    def handle(self, *args, **options):

        if options['multimedia']:
            Multimedia.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Multimedia, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Multimedia terminée!"))
        if options['ecu']:
            Ecu.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Ecu, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Ecu terminée!"))
        if options['corvet']:
            Corvet.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Corvet, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Corvet terminée!"))
