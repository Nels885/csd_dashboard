from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from squalaetp.models import Xelon, Indicator, ProductCategory, ProductCode, SparePart


class Command(BaseCommand):
    help = 'Clear Squalaetp tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xelon',
            action='store_true',
            dest='xelon',
            help='Clear Xelon table',
        )
        parser.add_argument(
            '--indicator',
            action='store_true',
            dest='indicator',
            help='Clear Indicator table',
        )
        parser.add_argument(
            '--prod_category',
            action='store_true',
            dest='prod_category',
            help='Clear ProductCategory table',
        )
        parser.add_argument(
            '--user_skills',
            action='store_true',
            dest='user_skills',
            help='Clear User Skills table',
        )
        parser.add_argument(
            '--parts',
            action='store_true',
            dest='parts',
            help='Delete all data in SparePart table',
        )
        parser.add_argument(
            '--part_relations',
            action='store_true',
            dest='part_relations',
            help='Delete relationships between ProductCode, Ecu and Media tables'
        )

    def handle(self, *args, **options):

        if options['xelon']:
            Xelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Xelon terminée!"))
        if options['indicator']:
            Indicator.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Indicator, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Indicator terminée!"))
        if options['prod_category']:
            ProductCategory.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ProductCategory, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table ProductCategory terminée!"))
        if options['user_skills']:
            ProductCategory.niv_t_users.through.objects.all().delete()
            ProductCategory.niv_i_users.through.objects.all().delete()
            ProductCategory.niv_l_users.through.objects.all().delete()
            ProductCategory.niv_u_users.through.objects.all().delete()
            ProductCategory.niv_o_users.through.objects.all().delete()
            ProductCategory.fa_users.through.objects.all().delete()
            ProductCategory.fe_users.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(
                no_style(), [
                    ProductCategory.niv_t_users.through, ProductCategory.niv_i_users.through,
                    ProductCategory.niv_l_users.through, ProductCategory.niv_u_users.through,
                    ProductCategory.niv_o_users.through, ProductCategory.fa_users.through,
                    ProductCategory.fe_users.through
                ]
            )
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données polyvavence produits terminée!"))
        if options['parts']:
            SparePart.objects.all().delete()
            ProductCode.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SparePart, ProductCode, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table SparePart terminée!"))
        if options['part_relations']:
            ProductCode.ecus.through.objects.all().delete()
            ProductCode.medias.through.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(
                no_style(), [ProductCode.ecus.through, ProductCode.medias.through])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(
                self.style.WARNING("Suppression des relations entre les tables ProductCode, Ecu et Media terminée!"))
