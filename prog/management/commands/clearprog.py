from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from prog.models import Raspeedi, Programing, AETLog, AETMeasure


class Command(BaseCommand):
    help = 'Clear Prog tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--raspeedi',
            action='store_true',
            dest='raspeedi',
            help='Clear Multimedia table',
        )
        parser.add_argument(
            '--programing',
            action='store_true',
            dest='programing',
            help='Clear Programing table',
        )
        parser.add_argument(
            '--aetlog',
            action='store_true',
            dest='aetlog',
            help='Clear AETLog table',
        )
        parser.add_argument(
            '--aetmeasure',
            action='store_true',
            dest='aetmeasure',
            help='Clear AETMeasure table',
        )

    def handle(self, *args, **options):
        message = "Deleting data from {0} table completed !"
        if options['raspeedi']:
            Raspeedi.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Raspeedi, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING(message.format('Raspeedi')))
        if options['programing']:
            Programing.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Programing, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING(message.format('Programing')))
        if options['aetlog']:
            AETLog.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [AETLog, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING(message.format('AETLog')))
        if options['aetmeasure']:
            AETMeasure.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [AETMeasure, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING(message.format('AETMeasure')))
