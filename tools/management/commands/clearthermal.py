from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from tools.models import ThermalChamber


class Command(BaseCommand):
    help = 'Clear ThermalChamber table'

    def handle(self, *args, **options):
        ThermalChamber.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ThermalChamber, ])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        for table in ["ThermalChamber"]:
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table {} terminée!".format(table)))
