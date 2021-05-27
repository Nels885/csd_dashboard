import os
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from constance import config

from tools.models import Suptech
from utils.conf import CSD_ROOT, string_to_list
from utils.django.models import defaults_dict

from ._file_suptech import CsvSuptech, ExcelSuptech, ExportExcelSuptech

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Suptech table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--first',
            action='store_true',
            dest='first',
            help='Adding first data in Suptech table',
        )
        parser.add_argument(
            '--email',
            action='store_true',
            dest='email',
            help='Send email for Suptech in progress',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SUPTECH] Waiting...")
        path = os.path.join(CSD_ROOT, "LOGS/LOG_SUPTECH")
        filename = "LOG_SUPTECH"
        try:
            if options['first']:
                excel = ExcelSuptech(os.path.join(path, filename + ".xls"))
                self._create(Suptech, excel.read())
            if options['email']:
                self._send_email()
            else:
                if os.path.exists(os.path.join(path, filename + ".csv")):
                    csv_file = CsvSuptech(os.path.join(path, filename + ".csv"))
                    self._create(Suptech, csv_file.read())
                    with open(os.path.join(path, filename + ".csv"), "w") as f:
                        f.write("DATE;QUI;XELON;ITEM;TIME;INFO;RMQ;;;;;\r\n")
                else:
                    self.stdout.write(self.style.WARNING("The file does not exist"))
                excel = ExcelSuptech(os.path.join(path, filename + ".xls"))
                self._update(Suptech, excel.read())
                self._export(path, filename)
        except FileNotFoundError as err:
            logger.error(f"[SUPTECH_CMD] FileNotFoundError: {err}")

    def _create(self, model, data):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in data:
            logger.info(row)
            try:
                defaults = defaults_dict(model, row)
                model.objects.create(**defaults)
                nb_prod_update += 1
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError: {}".format(err)))
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(row.get('item'), err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(row.get('item'), err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[SUPTECH] data create completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _update(self, model, data):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        queryset = model.objects.exclude(modified_at__isnull=False)
        for row in data:
            logger.info(row)
            user, xelon = row.get('user', ''), row.get('xelon', '')
            item, time = row.get('item', ''), row.get('time', '')
            action = row.pop('action', '')
            try:
                obj = queryset.get(**row)
                obj.action = action
                obj.save()
                nb_prod_update += 1
            except model.MultipleObjectsReturned as err:
                self.stdout.write(
                    self.style.WARNING(f"MultipleObjectsReturned: {user} {xelon} {item} {time} - {err}"))
            except model.DoesNotExist as err:
                self.stdout.write(
                    self.style.WARNING(f"DoesNotExist, modified in Dashboard: {user} {xelon} {item} {time} - {err}"))
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError: {}".format(err)))
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(item, err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(item, err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[SUPTECH] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _export(self, path, filename):
        header = [
            'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR'
        ]
        try:
            queryset = Suptech.objects.all().order_by('date')

            values_list = queryset.values_list(
                'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action'
            ).distinct()

            error = ExportExcelSuptech(values_list=values_list, filename=filename + ".xls", header=header,
                                       novalue="").file(path, False)
            if error:
                self.stdout.write(
                    self.style.ERROR(
                        "[SUPTECH] Export error because {}.xls file is read-only!".format(
                            os.path.join(path, filename)
                        )
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "[SUPTECH] Export completed: NB_FILE = {} | FILE = {}.xls".format(
                            queryset.count(), os.path.join(path, filename)
                        )
                    )
                )
        except FileNotFoundError as err:
            self.stdout.write(self.style.ERROR("[SUPTECH] {}".format(err)))

    def _send_email(self):
        date_joined = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
        subject = "Liste des Suptech en cours {}".format(date_joined)
        suptechs = Suptech.objects.exclude(status="Cloturée").order_by('-date')
        if suptechs:
            waiting_suptechs = suptechs.filter(status="En Attente")
            progress_suptechs = suptechs.filter(status="En Cours")
            html_message = render_to_string(
                'tools/email_format/suptech_list_email.html',
                {
                    'waiting_suptechs': waiting_suptechs, 'progress_suptechs': progress_suptechs,
                    'domain': config.WEBSITE_DOMAIN,
                }
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject, plain_message, None, string_to_list(config.SUPTECH_TO_EMAIL_LIST),
                html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des Suptech en cours terminée !"))
        else:
            self.stdout.write(self.style.SUCCESS("Pas de Suptech en cours à envoyer !"))
