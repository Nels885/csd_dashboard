from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.db.models import F

from constance import config

from dashboard.models import Contract
from squalaetp.models import Xelon, Indicator
from utils.conf import string_to_list
from utils.data.analysis import ProductAnalysis
from utils.django.validators import VIN_PSA_REGEX
from ._excel_contract import ExportExcelContract


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
            '--pending_products',
            action='store_true',
            dest='pending_products',
            help='Send email for pending products',
        )
        parser.add_argument(
            '--vin_error',
            action='store_true',
            dest='vin_error',
            help='Send email for VIN error',
        )
        parser.add_argument(
            '--vin_corvet',
            action='store_true',
            dest='vin_corvet',
            help='Send email for VIN no CORVET',
        )
        parser.add_argument(
            '--reman',
            action='store_true',
            dest='reman',
            help='Send email for REMAN in progress',
        )
        parser.add_argument(
            '--contract',
            action='store_true',
            dest='contract',
            help='Send email for Contract',
        )

    def handle(self, *args, **options):
        date_joined = timezone.datetime.strftime(timezone.localtime(), "%d/%m/%Y %H:%M:%S")
        last_7_days = timezone.datetime.today() - timezone.timedelta(7)
        first_90_days = timezone.datetime.today() + timezone.timedelta(90)
        data = {'domain': config.WEBSITE_DOMAIN}
        if options['late_products']:
            subject = 'Stocks et Retards {}'.format(date_joined)
            prods, data = self._product_header(data)
            data.update(prods.late_products())
            data.update({'filter': 'late', 'link_name': 'Lien vers la liste des produits en retard'})
            html_message = render_to_string('dashboard/email_format/lp_email.html', data)
            plain_message = strip_tags(html_message)
            send_mail(
                subject, plain_message, None, string_to_list(config.LATE_PRODUCTS_TO_EMAIL_LIST),
                html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des produits en retard terminée!"))
        if options['pending_products']:
            subject = 'Produits en cours {}'.format(date_joined)
            prods, data = self._product_header(data)
            data.update(prods.pending_products())
            data.update({'filter': 'pending', 'link_name': 'Lien vers la liste des produits en cours'})
            html_message = render_to_string('dashboard/email_format/lp_email.html', data)
            plain_message = strip_tags(html_message)
            send_mail(
                subject, plain_message, None, string_to_list(config.PENDING_PRODUCTS_TO_EMAIL_LIST),
                html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS("Envoi de l'email des produits en cours terminée!"))
        if options['vin_error']:
            subject = "Erreur VIN Xelon {}".format(date_joined)
            xelons = Xelon.objects.filter(vin_error=True, date_retour__gte=last_7_days).order_by('-date_retour')[:10]

            if xelons:
                html_message = render_to_string(
                    'dashboard/email_format/vin_error_email.html', {'xelons': xelons, 'domain': config.WEBSITE_DOMAIN}
                )
                plain_message = strip_tags(html_message)
                send_mail(
                    subject, plain_message, None, string_to_list(config.VIN_ERROR_TO_EMAIL_LIST),
                    html_message=html_message
                )
                self.stdout.write(self.style.SUCCESS("Envoi de l'email des erreurs de VIN terminée !"))
            else:
                self.stdout.write(self.style.SUCCESS("Pas d'erreurs de VIN a envoyer !"))
        if options['vin_corvet']:
            subject = "Problème CORVET {}".format(date_joined)
            xelons = Xelon.objects.filter(date_retour__gte=last_7_days, vin__regex=VIN_PSA_REGEX,
                                          vin_error=False, corvet__isnull=True).order_by('-date_retour')[:10]
            if xelons:
                html_message = render_to_string(
                    'dashboard/email_format/vin_corvet_email.html', {'xelons': xelons, 'domain': config.WEBSITE_DOMAIN}
                )
                plain_message = strip_tags(html_message)
                send_mail(
                    subject, plain_message, None, string_to_list(config.VIN_ERROR_TO_EMAIL_LIST),
                    html_message=html_message
                )
                self.stdout.write(self.style.SUCCESS("Envoi de l'email des VINs sans données CORVET terminée !"))
            else:
                self.stdout.write(self.style.SUCCESS("Pas de VIN sans données CORVET à envoyer !"))
        if options['contract']:
            subject = f"Contracts à renouveler {date_joined}"
            contracts = Contract.objects.filter(is_active=True, renew_date__lte=first_90_days)
            if contracts:
                contracts = contracts.annotate(excel_nb=F('id') + 1)
                attachment = self._excel_contract_generate(contracts)
                data.update({'obj': contracts})
                message = render_to_string('dashboard/email_format/contract_email.html', data)
                email = EmailMessage(
                    subject=subject, body=message, from_email=None, to=string_to_list(config.CONTRACT_TO_EMAIL_LIST),
                )
                email.attach_file(path=attachment, mimetype='application/octet-stream')
                email.send()
                self.stdout.write(self.style.SUCCESS("Envoi de l'email des contrats terminée !"))
            else:
                self.stdout.write(self.style.SUCCESS("Pas de contracts a envoyer !"))
        if options['reman']:
            call_command("emailreman", "--batch")

    @staticmethod
    def _product_header(data):
        prods = ProductAnalysis()
        indicator = Indicator.objects.filter(date=timezone.now()).first()
        if indicator:
            data.update({
                'products_to_repair': indicator.products_to_repair,
                'late_products': indicator.late_products,
                'express_products': indicator.express_products,
                'vip_products': prods.vip
            })
        return prods, data

    @staticmethod
    def _excel_contract_generate(queryset):
        excel = ExportExcelContract()
        filename = f"Contrats_a_renouveler_au_{excel.date.strftime('%y-%m-%d_%H-%M')}"
        excel.header = [
            'N° ligne Excel', 'Service', 'Nature du document', 'Objet du document', 'Fournisseur', 'Site', 'Date fin',
            'Contract actif', 'Date prévenance'
        ]
        fields = [
            'excel_nb', 'service', 'nature', 'object', 'supplier', 'site', 'end_date', 'is_active', 'renew_date'
        ]
        values_list = queryset.values_list(*fields)
        return excel.file(filename, "xlsx", values_list)
