from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from squalaetp.models import Xelon, CorvetBackup, Corvet
from raspeedi.models import Raspeedi
from utils.conf import XLS_SQUALAETP_FILE

from ._excel_squalaetp import ExcelSqualaetp


class Command(BaseCommand):
    help = 'Interact with the Squalaetp tables in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--relations',
            action='store_true',
            dest='relations',
            help='add the relationship between the xelon and corvet tables',
        )
        parser.add_argument(
            '--del_relations',
            action='store_true',
            dest='del_relations',
            help='delete all relations',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Squalaetp tables',
        )

    def handle(self, *args, **options):

        if options['relations']:
            if options['filename'] is not None:
                excel = ExcelSqualaetp(options['filename'])
            else:
                excel = ExcelSqualaetp(XLS_SQUALAETP_FILE)
            self.stdout.write("Nombre de ligne dans Excel:     {}".format(excel.nrows))
            # self.stdout.write("Noms des colonnes:              {}".format(excel.columns))

            count, objects_list = 0, []
            for xelon in Xelon.objects.all():
                try:
                    corvet = Corvet.objects.get(pk=xelon.vin)
                    corvet.xelons.add(xelon)
                    count += 1
                except ObjectDoesNotExist:
                    objects_list.append(xelon.numero_de_dossier)
            # self.stdout.write("pas de relation pour les dossier Xelon suivant:\n{}".format(objects_list))
            self.stdout.write("Nombre de relations Corvet/Xelon ajoutées: {}".format(count))
            count, objects_list = 0, []
            for corvet in Corvet.objects.all():
                try:
                    for cal in [corvet.electronique_14x, corvet.electronique_94x]:
                        if cal is not None and len(cal) == 10:
                            raspeedi = Raspeedi.objects.get(pk=int(cal))
                            raspeedi.corvets.add(corvet)
                            count += 1
                except ObjectDoesNotExist:
                    objects_list.append(corvet.electronique_14x)

            # self.stdout.write("pas de relation pour les boitiers Corvet suivant:\n{}".format(objects_list))
            self.stdout.write("Nombre de relations Raspeedi/Corvet ajoutées: {}".format(count))

        elif options['del_relations']:
            Corvet.xelons.through.objects.all().delete()
            Raspeedi.corvets.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(),
                                                             [Corvet.xelons.through, Raspeedi.corvets.through, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write("Suppression des relations des tables Xelon, Corvet, Raspeedi terminée!")

        elif options['delete']:
            Xelon.objects.all().delete()
            Corvet.objects.all().delete()
            Corvet.xelons.through.objects.all().delete()
            CorvetBackup.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, Corvet, CorvetBackup, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Xelon", "Corvet", "CorvetBackup"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))
