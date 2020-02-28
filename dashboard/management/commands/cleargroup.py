from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Clear Group table'

    def handle(self, *args, **options):
        Group.objects.all().delete()
        Group.permissions.through.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Group, Group.permissions.through, ])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        for table in ["Group"]:
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))
