import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError

from psa.models import EmfModel, Ecu
from reman.models import EcuType

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Corvet table in the database'

    def handle(self, *args, **options):
        self.stdout.write("[MIGRATE_PSA] Waiting...")

        for emf in EmfModel.objects.all().order_by('id'):
            Ecu.objects.update_or_create(
                pk=emf.id,
                comp_ref=emf.hw_reference,
                name=emf.name,
                type='EMF',
                hw=emf.hw,
                sw=emf.sw,
                supplier_oe=emf.supplier_oe,
                pr_reference=emf.pr_reference
            )

        cmm_id = Ecu.objects.filter(type='EMF').latest('id').id + 1

        self.stdout.write("[MIGRATE_EMF] complete!")

        for cmm in EcuType.objects.all().order_by('id'):
            try:
                if len(cmm.hw_reference) == 10:
                    Ecu.objects.update_or_create(
                        pk=cmm_id,
                        comp_ref=cmm.hw_reference,
                        name=cmm.technical_data,
                        type='CMM',
                        supplier_oe=cmm.supplier_oe,
                    )
                    cmm_id += 1
            except Ecu.DoesNotExist:
                self.stdout.write(f"DoesNotExist : {cmm.hw_reference}")
            except IntegrityError as err:
                self.stdout.write(f"IntegrityError: {err}")
            except DataError as err:
                self.stdout.write(f"DataError: {cmm.hw_reference} - {err}")

        self.stdout.write("[MIGRATE_CMM] complete!")
