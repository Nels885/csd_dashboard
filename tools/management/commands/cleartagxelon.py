from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from tools.models import TagXelon


class Command(BaseCommand):
    help = 'Clear TagXelonMulti table'

    def handle(self, *args, **options):
        TagXelon.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [TagXelon, ])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        for table in ["TagXelon"]:
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))
