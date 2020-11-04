from django.core.management.base import BaseCommand
from django.utils import timezone, formats
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from constance import config

from utils.conf import string_to_list
from utils.data.analysis import ProductAnalysis


class Command(BaseCommand):
    help = 'Send email for Late products'

    def handle(self, *args, **options):
        date_joined = formats.date_format(timezone.now(), "SHORT_DATETIME_FORMAT")
        subject = 'Stocks et Retards {}'.format(date_joined)
        prods = ProductAnalysis()
        prods = prods.late_products().order_by('-delai_au_en_jours_ouvres')
        psa = prods.filter(ilot='PSA')
        clarion = prods.filter(ilot='CLARION')
        labo_qual = prods.filter(ilot='LaboQual')
        ilot_autre = prods.filter(ilot='ILOTAUTRE')
        defaut = prods.filter(ilot='DEFAUT')
        html_message = render_to_string('dashboard/late_products/lp_email.html', {
            'psa': psa,
            'clarion': clarion,
            'labo_qual': labo_qual,
            'ilot_autre': ilot_autre,
            'defaut': defaut
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, None, string_to_list(config.TO_LATE_PRODUCTS_EMAIL_LIST),
            html_message=html_message
        )
        self.stdout.write(self.style.SUCCESS("Envoi de l'email des produits en retard terminée!"))
