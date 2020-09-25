from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.db.utils import DataError, IntegrityError

from squalaetp.models import ProductCode, Stock
from reman.models import EcuRefBase, EcuModel, SparePart, EcuType
from utils.conf import XLS_ECU_REF_BASE, CSD_ROOT
from utils.file.export import ExportExcel, os

from ._excel_reman import ExcelEcuRefBase

import logging as log


class Command(BaseCommand):
    help = 'Interact with the EcuRefBase table in the database'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '-s',
            '--sheet_id',
            type=int,
            default=0
        )
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--export',
            action='store_true',
            dest='export',
            help='Export all data of EcuRefBase',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in EcuRefBase table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[ECUREFBASE] Waiting...")

        if options['delete']:
            EcuRefBase.objects.all().delete()
            EcuModel.objects.all().delete()
            EcuType.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(),
                                                             [EcuRefBase, EcuModel, EcuType])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table EcuRefBase terminée!"))
        elif options['export']:
            filename = 'base_ref_reman_new'
            path = os.path.join(CSD_ROOT, "EXTS")
            header = [
                'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR',
                'REF CAL',
                'REF à créer '
            ]
            ecus = EcuModel.objects.all().order_by('ecu_type__ecu_ref_base__reman_reference')
            values_list = (
                'oe_raw_reference', 'ecu_type__ecu_ref_base__reman_reference', 'ecu_type__technical_data',
                'ecu_type__hw_reference', 'ecu_type__supplier_oe', 'psa_barcode', 'former_oe_reference', 'sw_reference',
                'ecu_type__spare_part__code_produit'
            )
            ExportExcel(queryset=ecus, filename=filename, header=header, values_list=values_list).file(path)
            self.stdout.write(
                self.style.SUCCESS(
                    "Export ECU_REF_BASE completed: NB_REF = {} | FILE = {}.csv".format(ecus.count(), filename))
            )
        else:
            if options['filename'] is not None:
                extraction = ExcelEcuRefBase(options['filename'], sheet_name=options['sheet_id'])
            else:
                extraction = ExcelEcuRefBase(XLS_ECU_REF_BASE, sheet_name=options['sheet_id'])

            nb_base_before, nb_ecu_before = EcuRefBase.objects.count(), EcuModel.objects.count()
            nb_base_update, nb_ecu_update, nb_part_update, nb_type_update = 0, 0, 0, 0
            for row in extraction.read_all():
                log.info(row)
                reman_reference = row.pop("reman_reference")
                type_values = dict(
                    (key, value) for key, value in row.items() if key in ["technical_data", "supplier_oe"]
                )
                for key in ["technical_data", "supplier_oe"]:
                    del row[key]
                code_produit = row.pop("code_produit")
                try:
                    # Update or Create SpareParts
                    part_obj, part_created = SparePart.objects.update_or_create(
                        code_produit=code_produit, defaults={
                            "code_zone": "REMAN PSA", "code_magasin": "MAGREM PSA"
                        }
                    )
                    if not part_created:
                        nb_part_update += 1

                    # Update or create StockParts
                    prod_obj, part_created = ProductCode.objects.get_or_create(
                        name=code_produit)
                    stock_obj, stock_created = Stock.objects.update_or_create(
                        code_magasin="MAGREM PSA", code_zone="REMAN PSA", code_produit=prod_obj
                    )

                    # Update or Create EcuType
                    type_values['spare_part'] = part_obj
                    type_obj, type_created = EcuType.objects.update_or_create(
                        hw_reference=row.pop("hw_reference"), defaults=type_values
                    )
                    if not type_created:
                        nb_type_update += 1

                    # Update or Create EcurefBase
                    base_obj, base_created = EcuRefBase.objects.update_or_create(
                        reman_reference=reman_reference, defaults={"ecu_type": type_obj})
                    if not base_created:
                        nb_base_update += 1

                    # Update or Create Ecumodel
                    row['ecu_type'] = type_obj
                    ecu_obj, ecu_created = EcuModel.objects.update_or_create(
                        psa_barcode=row.pop("psa_barcode"), defaults=row
                    )
                    if not ecu_created:
                        nb_ecu_update += 1
                except DataError as err:
                    print("DataError: {} - {}".format(reman_reference, err))
                except IntegrityError as err:
                    print("IntegrityError: {} - {}".format(reman_reference, err))
                except Stock.MultipleObjectsReturned as err:
                    print("MultipleObjectsReturned: {} - {}".format(code_produit, err))

            nb_base_after, nb_ecu_after = EcuRefBase.objects.count(), EcuModel.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[ECUREFBASE] Data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_base_after - nb_base_before, nb_base_update, nb_base_after
                    )
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "[ECUMODEL] Data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_ecu_after - nb_ecu_before, nb_ecu_update, nb_ecu_after
                    )
                )
            )
