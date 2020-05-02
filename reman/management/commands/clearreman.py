from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from reman.models import SparePart, Repair, Batch, EcuModel


class Command(BaseCommand):
    help = 'Clear REMAN tables'

    def handle(self, *args, **options):
        SparePart.objects.all().delete()
        EcuModel.objects.all().delete()
        Repair.objects.all().delete()
        Batch.objects.all().delete()
        SparePart.repairs.through.objects.all().delete()

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SparePart, EcuModel, Repair, Batch,
                                                                      SparePart.repairs.through])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS("Suppression des données des tables REMAN terminée!"))
