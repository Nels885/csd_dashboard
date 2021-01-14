from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from squalaetp.models import Xelon


class Command(BaseCommand):
    help = 'Clear Squalaetp tables'

    def handle(self, *args, **options):
        Xelon.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, ])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS("Suppression des données des tables Squalaetp terminée!"))
