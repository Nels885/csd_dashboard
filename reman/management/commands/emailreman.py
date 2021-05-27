from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q, Count, F

from constance import config

from reman.models import Batch
from utils.conf import string_to_list


class Command(BaseCommand):
    help = 'Send email for Bach in progress'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            action='store_true',
            dest='batch',
            help='Send email for Batch in progress',
        )

    def handle(self, *args, **options):
        date_joined = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
        next_7_days = timezone.datetime.today() + timezone.timedelta(7)
        if options['batch']:
            self._batch_email(date_joined, next_7_days)

    def _batch_email(self, date_joined, next_7_days):
        subject = "Liste des lots REMAN en cours {}".format(date_joined)
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        batchs = Batch.objects.filter(active=True, number__lt=900)
        if batchs:
            batchs = batchs.annotate(repaired=repaired, packed=packed, remaining=F('quantity') - repaired)
            current_batchs = batchs.filter(start_date__lte=timezone.now()).order_by('end_date')
            next_batchs = batchs.filter(start_date__gt=timezone.now(), start_date__lte=next_7_days).order_by('end_date')
            html_message = render_to_string(
                'reman/email_format/reman_batches_email.html',
                {
                    'current_batchs': current_batchs, 'next_batchs': next_batchs, 'domain': config.WEBSITE_DOMAIN,
                    'current_date': timezone.now().date()
                }
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject, plain_message, None, string_to_list(config.REMAN_TO_EMAIL_LIST),
                html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des lots REMAN en cours terminée !"))
        else:
            self.stdout.write(self.style.SUCCESS("Pas de lot REMAN en cours à envoyer !"))
