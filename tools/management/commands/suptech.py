import logging
from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from constance import config

from squalaetp.models import Xelon
from tools.models import Suptech
from utils.conf import string_to_list

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Suptech table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            dest='email',
            help='Send email for Suptech in progress',
        )
        parser.add_argument(
            '--email_48h',
            action='store_true',
            dest='email_48h',
            help='Send email processing 48h for Suptech'
        )
        parser.add_argument(
            '--email_48h_late',
            action='store_true',
            dest='email_48h_late',
            help='Send email processing 48h late for Suptech'
        )
        parser.add_argument(
            '--email_graph',
            action='store_true',
            dest='email_graph',
            help='Send email graph for Suptech'
        )
        parser.add_argument(
            '--prod_update',
            action='store_true',
            dest='prod_update',
            help='Update product Xelon for Suptech'
        )

    def handle(self, *args, **options):
        self.stdout.write("[SUPTECH] Waiting...")
        if options['email']:
            date_joined = timezone.datetime.strftime(timezone.localtime(), "%d/%m/%Y %H:%M:%S")
            suptechs = Suptech.objects.exclude(Q(status__in=["Cloturée", "Annulée"]) | Q(is_48h=False)).order_by('-date')
            supject = "Suptech non 48h en attente au {}".format(date_joined)
            self._send_email(queryset=suptechs, subject=supject, to_email=config.SUPTECH_TO_EMAIL_LIST)
        if options['email_48h']:
            suptechs = Suptech.objects.exclude(Q(status="Cloturée") | Q(status="Annulée")).filter(
                Q(is_48h=True) | Q(deadline=timezone.now())).order_by('-date')
            for suptech in suptechs:
                self._send_single_email(suptech)
        if options['email_48h_late']:
            date_joined = timezone.datetime.strftime(timezone.localtime(), "%d/%m/%Y %H:%M:%S")
            supject = "Suptech 48h en retard {}".format(date_joined)
            more_48h = timezone.datetime.today() + timezone.timedelta(2)
            suptechs = Suptech.objects.exclude(
                Q(date__gt=more_48h) | Q(status="Cloturée") | Q(status="Annulée")).filter(
                Q(is_48h=True) | Q(deadline=timezone.now())).order_by('-date')
            self._send_48h_late_email(queryset=suptechs, subject=supject, to_email=config.SUPTECH_CC_EMAIL_LIST)
        if options['email_graph']:
            date_joined = timezone.datetime.strftime(timezone.localtime(), "%d/%m/%Y %H:%M:%S")
            supject = "Suptech graphique {}".format(date_joined)
            suptechs = Suptech.objects.exclude(Q(status="Cloturée") | Q(category=3)).order_by('-date')
            self._send_email(queryset=suptechs, subject=supject, to_email=config.SUPTECH_TO_EMAIL_LIST)
        if options['prod_update']:
            suptechs = Suptech.objects.exclude(xelon__isnull=True)
            for suptech in suptechs:
                try:
                    product = Xelon.objects.get(numero_de_dossier=suptech.xelon).modele_produit
                    suptech.product = product
                    suptech.save()
                except Xelon.DoesNotExist:
                    pass
            self.stdout.write(self.style.SUCCESS("[SUPTECH] Update xelon product completed."))

    def _send_email(self, queryset, subject, to_email):
        if queryset:
            waiting_suptechs = queryset.filter(status="En Attente")
            progress_suptechs = queryset.filter(status="En Cours")
            html_message = render_to_string(
                'tools/email_format/suptech_list_email.html',
                {
                    'waiting_suptechs': waiting_suptechs, 'progress_suptechs': progress_suptechs,
                    'domain': config.WEBSITE_DOMAIN,
                }
            )
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, None, string_to_list(to_email), html_message=html_message)
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des Suptech en cours terminée !"))
        else:
            self.stdout.write(self.style.SUCCESS("Pas de Suptech en cours à envoyer !"))

    def _send_single_email(self, query):
        domain = config.WEBSITE_DOMAIN
        days_late = (timezone.now().date() - query.date).days
        subject = f"[SUPTECH_{query.id} !!RAPPEL_{days_late}J!!] {query.item}"
        to_list = list(set(string_to_list(f"{query.to}; {query.category.to}")))
        cc_list = list(set(string_to_list(f"{query.cc}; {query.category.cc}")))
        try:
            email = query.created_by.email
        except AttributeError:
            email = "No Found"
        context = {'email': email, 'suptech': query, 'domain': domain}
        message = render_to_string('tools/email_format/suptech_request_email.html', context)
        EmailMessage(subject=subject, body=message, from_email=None, to=to_list, cc=cc_list).send()
        self.stdout.write(self.style.SUCCESS(f"Envoi de l'email Suptech n°{query.id} en attente terminée !"))

    def _send_48h_late_email(self, queryset, subject, to_email):
        if queryset:
            co_suptechs = queryset.filter(category__name="Cellule Operation")
            ce_suptechs = queryset.filter(category__name="Cellule Etude")
            process_suptechs = queryset.filter(category__name="Modif. process")
            html_message = render_to_string(
                'tools/email_format/suptech_list_48h_late_email.html',
                {
                    'co_suptechs': co_suptechs, 'process_suptechs': process_suptechs,
                    'ce_suptechs': ce_suptechs, 'domain': config.WEBSITE_DOMAIN,
                }
            )
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, None, string_to_list(to_email), html_message=html_message)
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des Suptech en retard terminée !"))
        else:
            self.stdout.write(self.style.SUCCESS("Pas de Suptech en retard à envoyer !"))
