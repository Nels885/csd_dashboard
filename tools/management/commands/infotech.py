import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from constance import config

from tools.models import Infotech
from utils.conf import string_to_list

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Infotech table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            dest='email',
            help='Send email for Suptech in progress',
        )

    def handle(self, *args, **options):
        self.stdout.write("[INFOTECH] Waiting...")
        if options['email']:
            queryset = Infotech.objects.exclude(Q(status="Cloturée")).order_by('-created_at')
            if queryset:
                for query in queryset:
                    self._send_single_email(query)
            else:
                self.stdout.write(self.style.SUCCESS("Pas d'Infotech en cours à envoyer !"))

    def _send_single_email(self, query):
        days_late = (timezone.now() - query.created_at).days
        subject = f"[INFOTECH_{query.id} !!RAPPEL_{days_late}J!!] {query.item}"
        to_list = string_to_list(query.to)
        cc_list = string_to_list(query.cc)
        try:
            email = query.created_by.email
            cc_list = list(set(string_to_list(f"{query.cc}; {email}")))
        except AttributeError:
            email = "No Found"
        context = {'email': email, 'instance': query, 'domain': config.WEBSITE_DOMAIN}
        message = render_to_string('tools/email_format/infotech_email.html', context)
        EmailMessage(subject=subject, body=message, from_email=None, to=to_list, cc=cc_list).send()
        self.stdout.write(self.style.SUCCESS(f"Envoi de l'email Infotech n°{query.id} en cours terminée !"))
