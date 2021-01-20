from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from constance import config

from squalaetp.models import Xelon
from utils.conf import string_to_list
from utils.data.analysis import ProductAnalysis


class Command(BaseCommand):
    help = 'Send email for Late products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--late_products',
            action='store_true',
            dest='late_products',
            help='Send email for late products',
        )
        parser.add_argument(
            '--vin_error',
            action='store_true',
            dest='vin_error',
            help='Send email for VIN error',
        )

    def handle(self, *args, **options):
        date_joined = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
        if options['late_products']:
            subject = 'Stocks et Retards {}'.format(date_joined)
            prods = ProductAnalysis()
            data = prods.late_products()

            html_message = render_to_string(
                'dashboard/email_format/lp_email.html', data)
            plain_message = strip_tags(html_message)
            send_mail(
                subject, plain_message, None, string_to_list(config.LATE_PRODUCTS_TO_EMAIL_LIST),
                html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des produits en retard terminée!"))
        elif options['vin_error']:
            last_7_days = timezone.datetime.today() - timezone.timedelta(7)
            subject = "Liste d'erreur de VIN Xelon {}".format(date_joined)
            xelons = Xelon.objects.filter(vin_error=True, date_retour__gte=last_7_days).order_by('-date_retour')[:10]

            if xelons:
                html_message = render_to_string('dashboard/email_format/vin_error_email.html', {'xelons': xelons})
                plain_message = strip_tags(html_message)
                send_mail(
                    subject, plain_message, None, string_to_list(config.VIN_ERROR_TO_EMAIL_LIST),
                    html_message=html_message
                )
                self.stdout.write(self.style.SUCCESS("Envoi de l'email des erreurs de VIN terminée !"))
            else:
                self.stdout.write(self.style.SUCCESS("Pas d'erreurs de VIN a envoyer !"))
