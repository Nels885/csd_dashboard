from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from psa.models import Multimedia, Ecu, Corvet, CorvetAttribute, DefaultCode, CanRemote


class Command(BaseCommand):
    help = 'Clear Psa tables'

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
            help='Clear Corvet table',
        )
        parser.add_argument(
            '--dtc',
            action='store_true',
            dest='dtc',
            help='Clear defaultCode table',
        )
        parser.add_argument(
            '--corvet_attribute',
            action='store_true',
            dest='corvet_attribute',
            help='Clear CorvetAttribute table',
        )
        parser.add_argument(
            '--canremote',
            action='store_true',
            dest='canremote',
            help='Clear CanRemote table',
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
        if options['dtc']:
            DefaultCode.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [DefaultCode, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table DefaultCode terminée!"))
        if options['corvet_attribute']:
            CorvetAttribute.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CorvetAttribute, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table CorvetAttribute terminée!"))
        if options['canremote']:
            CanRemote.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CanRemote, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table CanRemote terminée!"))
