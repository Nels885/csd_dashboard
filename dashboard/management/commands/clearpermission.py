from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Clear Permission table'

    def handle(self, *args, **options):
        Permission.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Permission, ])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        for table in ["Permission"]:
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))
