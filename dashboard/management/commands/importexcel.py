import os
import re
import logging
from io import StringIO
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from constance import config

from utils.conf import string_to_list
from utils.conf import CSD_ROOT

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the all tables in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tests',
            action='store_true',
            dest='tests',
            help='Send Email of tests',
        )

    def handle(self, *args, **options):
        out = StringIO()
        self.stdout.write("[IMPORT_EXCEL] Waiting...")
        call_command("loadraspeedi", stdout=out)
        call_command("programing", stdout=out)
        call_command("loadsqualaetp", stdout=out)
        call_command("importcorvet", "--squalaetp", stdout=out)
        call_command("exportsqualaetp")
        call_command("loadsqualaetp", "--relations")
        if "Error" in out.getvalue() or options['tests']:
            cleaned = re.sub(r"\[[\d;]+[a-z]", "", out.getvalue())
            subject = "[CSD_DASHBOARD] Rapport d'erreurs système"
            if options['tests']:
                subject = "[CSD_DASHBOARD] Rapport de tests système"
            self._send_email(subject, cleaned)

        self.stdout.write(self.style.SUCCESS("[IMPORT_EXCEL] Update completed."))

    def _send_email(self, subject, data):
        context = {
            "network": self._dir_check(), "raspeedi": [], "squalaetp": [], "delay": [], "limit": [], "corvet": []
        }
        for line in data.split("\n"):
            if "RASPEEDI_FILE" in line:
                context["raspeedi"].append(line)
            if "SQUALAETP_FILE" in line:
                context["squalaetp"].append(line)
            if "DELAY_FILE" in line:
                context["delay"].append(line)
            if "TIME_LIMIT_FILE" in line:
                context["limit"].append(line)
            if "CorvetError in" in line:
                context["corvet"].append(line)

        html_message = render_to_string('dashboard/email_format/check_commands.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, None, string_to_list(config.SYS_REPORT_TO_MAIL_LIST),
            html_message=html_message
        )
        self.stdout.write(self.style.SUCCESS("Envoi de l'email Erreur import Excel terminée !"))

    @staticmethod
    def _dir_check():
        data = [
            [r"L:\EXTS", os.path.join(CSD_ROOT, "EXTS"), "NG"],
            [r"L:\RH\AnalyseRetards", os.path.join(CSD_ROOT, "RH/AnalyseRetards"), "NG"],
            [r"L:\RH\Analyse_Delais", os.path.join(CSD_ROOT, "RH/Analyse_Delais"), "NG"],
            [r"L:\PROG\RASPEEDI", os.path.join(CSD_ROOT, "PROG/RASPEEDI"), "NG"]
        ]
        for i, values in enumerate(data):
            if os.path.exists(values[1]):
                data[i][2] = "OK"
        return data
