from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from volvo.models import SemRefBase, SemModel, SemType


class Command(BaseCommand):
    help = 'Clear Volvo tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--semrefbase',
            action='store_true',
            dest='semrefbase',
            help='Clear SemRefBase table',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Clear all tables',
        )

    def handle(self, *args, **options):

        if options['semrefbase']:
            SemRefBase.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SemRefBase])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table SemRefBase terminée!"))

        if options['all']:
            SemRefBase.objects.all().delete()
            SemModel.objects.all().delete()
            SemType.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SemRefBase, SemModel, SemType])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données des tables Volvo terminée!"))
