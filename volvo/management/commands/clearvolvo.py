from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from volvo.models import SemRefBase


class Command(BaseCommand):
    help = 'Clear Volvo tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--semrefbase',
            action='store_true',
            dest='semrefbase',
            help='Clear SemRefBase table',
        )

    def handle(self, *args, **options):

        if options['semrefbase']:
            SemRefBase.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SemRefBase])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table SemRefBase terminée!"))
