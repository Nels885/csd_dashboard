import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from squalaetp.models import ProductCategory

from ._excel_skill import ExcelUserSkill

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Stock table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '-s',
            '--sheet_name',
            dest='sheet_name',
            default="PSA",
            help='Specify Sheet Name',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SKILL] Waiting...")

        if options['filename'] is not None:
            skill = ExcelUserSkill(options['filename'], sheet_name=options['sheet_name'])
            nb_update = 0
            for row in skill.read():
                logger.info(row)
                try:
                    user = User.objects.get(last_name=row.pop("Nom"), first_name=row.pop("Prénom"))
                    for key, value in row.items():
                        for query in ProductCategory.objects.filter(product_model__contains=key):
                            if value == "I":
                                query.niv_i_users.add(user)
                            elif value == "L":
                                query.niv_l_users.add(user)
                            elif value == "U":
                                query.niv_u_users.add(user)
                            elif value == "O":
                                query.niv_o_users.add(user)
                            query.save()
                    nb_update += 1
                except User.DoesNotExist:
                    pass
            self.stdout.write(self.style.SUCCESS(f"[SKILL] Data update completed:  UPDATE = {nb_update}"))
