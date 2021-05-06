from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from reman.models import SparePart, Repair, Batch, EcuModel, Default, EcuRefBase, EcuType


class Command(BaseCommand):
    help = 'Clear REMAN tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            action='store_true',
            dest='batch',
            help='Clear Batch table',
        )
        parser.add_argument(
            '--default',
            action='store_true',
            dest='default',
            help='Clear Default tables',
        )
        parser.add_argument(
            '--ecumodel',
            action='store_true',
            dest='ecumodel',
            help='Clear EcuModel table',
        )
        parser.add_argument(
            '--ecutype',
            action='store_true',
            dest='ecutype',
            help='Clear EcuType table',
        )
        parser.add_argument(
            '--ecurefbase',
            action='store_true',
            dest='ecurefbase',
            help='Clear EcuRefBase table',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Clear Reman tables',
        )

    def handle(self, *args, **options):

        if options['batch']:
            Batch.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Batch, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Batch terminée!"))

        if options['default']:
            Default.objects.all().delete()
            Default.ecu_type.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Default, Default.ecu_type.through, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Default terminée!"))

        if options['ecumodel']:
            EcuModel.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [EcuModel, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table EcuModel terminée!"))

        if options['ecutype']:
            EcuType.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [EcuType, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table EcuType terminée!"))

        if options['ecurefbase']:
            EcuRefBase.objects.all().delete()
            EcuModel.objects.all().delete()
            EcuType.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [EcuRefBase, EcuModel, EcuType])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table EcuRefBase terminée!"))

        if options['all']:
            SparePart.objects.all().delete()
            EcuType.objects.all().delete()
            EcuModel.objects.all().delete()
            EcuRefBase.objects.all().delete()
            Repair.objects.all().delete()
            Batch.objects.all().delete()
            Default.objects.all().delete()
            Default.ecu_type.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [
                SparePart, EcuType, EcuModel, EcuRefBase, Repair, Batch, Default, Default.ecu_type.through
            ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données des tables REMAN terminée!"))
