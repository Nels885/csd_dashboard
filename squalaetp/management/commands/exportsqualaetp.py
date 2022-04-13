import logging
from django.core.management.base import BaseCommand

from constance import config

from utils.conf import string_to_list
from squalaetp.models import Xelon
from psa.models import Corvet

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Export CSV file for Batch REMAN'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corvet',
            action='store_true',
            dest='corvet',
            help='Export all corvet',
        )

    def handle(self, *args, **options):
        if options['corvet']:
            self.stdout.write("[CORVET_EXPORT] Waiting...")

            filename = "squalaetp_corvet.csv"
            path = os.path.join(CSD_ROOT, "EXTS")
            header = [f.name for f in Corvet._meta.local_fields]
            queryset = Corvet.objects.exclude(donnee_date_entree_montage__isnull=True)
            values_list = queryset.values_list().distinct()
            ExportExcel(values_list=values_list, filename=filename, header=header).file(path, False)
            self.stdout.write(
                self.style.SUCCESS(
                    "[CORVET_EXPORT] Export completed: NB_BATCH = {} | FILE = {}".format(
                        queryset.count(), os.path.join(path, filename)
                    )
                )
            )
        else:
            self.stdout.write("[SQUALAETP_EXPORT] Waiting...")

            path = os.path.join(CSD_ROOT, "EXTS")
            header = [
                'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE',
                'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE', 'SILHOUETTE', 'GENRE_DE_PRODUIT',
                'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM', 'DQS', 'DRC', 'DRT', 'DTI',
                'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J', '14K', '14L', '14R',
                '14X', '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F', '94L', '94X',
                'DAT', 'DCX', '19H', '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A', '64A',
                '84A', '94A', 'P4A', 'MOTEUR', 'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B',
                '16P', '46P', '56P', '66P', '16B', '46B', '56B', '66B', '86B', '96B',
                'DAO', 'DCD', 'DE2', 'DE3', 'DE4', 'DPR', 'DQK', 'DQP', 'DUB', 'DUE', 'DUF', 'DYC', 'DYQ', 'DZE', '94R',
                '16Q', '96Q', '16V', '19F', '19U', '14D', '94D', '16G', '96G', '94J', '94K', '19V', '12Y', '92Y', '16L',
                '96L', '14Y', '14Z', '14P', '94P', '34P', '19W', '16T', '19T', '14M', '94M', '18Z', '11M', '19K', '49K',
                '59K', '69K', '99K', '12E', '42E', '52E', '62E', '92E', 'K9H', 'M9H', 'R9H', 'T2Y', 'D5J', 'DAZ', 'DCP',
                'DDC', 'DE7', 'DE8', 'DES', 'DI2', 'DJZ', 'DN1', 'DSB', 'DUO', 'DUZ',
                'TELECODAGE', 'APPAIRAGE'
            ]
            try:
                queryset = Xelon.objects.filter(is_active=True).distinct()

                corvet_list = tuple([f"corvet__{field.name}" for col_nb, field in enumerate(Corvet._meta.fields) if
                                     col_nb < (len(header) - 5) and field.name not in ['vin']])
                xelon_list = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule')
                extra_list = ('telecodage', 'appairage')

                values_list = queryset.values_list(*(xelon_list + corvet_list + extra_list)).distinct()
                for filename in string_to_list(config.SQUALAETP_FILE_LIST):
                    error = ExportExcel(
                        values_list=values_list, filename=filename, header=header).file(path, False)
                    if error:
                        self.stdout.write(
                            self.style.ERROR(
                                "[SQUALAETP_EXPORT] Export error because {} file is read-only!".format(
                                    os.path.join(path, filename)
                                )
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                "[SQUALAETP_EXPORT] Export completed: NB_FILE = {} | FILE = {}".format(
                                    queryset.count(), os.path.join(path, filename)
                                )
                            )
                        )
            except FileNotFoundError as err:
                self.stdout.write(self.style.ERROR("[SQUALAETP_EXPORT] {}".format(err)))
                logger.error(f"FileNotFoundError: {err}")
