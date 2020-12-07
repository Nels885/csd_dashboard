from django.core.management.base import BaseCommand
from django.utils import timezone, formats
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from constance import config

from utils.conf import string_to_list
from squalaetp.models import Xelon


class Command(BaseCommand):
    help = 'Send email for VIN error'

    def handle(self, *args, **options):
        date_joined = formats.date_format(timezone.now(), "SHORT_DATETIME_FORMAT")
        last_7_days = timezone.datetime.today() - timezone.timedelta(7)
        subject = "Liste d'erreur de VIN Xelon {}".format(date_joined)
        xelons = Xelon.objects.filter(vin_error=True, date_retour__gte=last_7_days).order_by('-date_retour')[:10]

        html_message = render_to_string('dashboard/vin_error_email.html', {'xelons': xelons})
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, None, string_to_list(config.VIN_ERROR_TO_EMAIL_LIST),
            html_message=html_message
        )
        self.stdout.write(self.style.SUCCESS("Envoi de l'email des erreurs de VIN terminée!"))
