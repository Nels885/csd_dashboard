from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.contrib.auth.models import ContentType


class Command(BaseCommand):
    help = 'Clear Django tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Clear Django tables',
        )

    def handle(self, *args, **options):
        if options['all']:
            ContentType.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ContentType, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Completed deleting data from Django tables !"))
