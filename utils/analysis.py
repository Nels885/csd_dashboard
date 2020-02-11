from django.db.models.aggregates import Count

from squalaetp.models import Xelon, Corvet
import datetime


# import itertools


class ProductAnalysis:
    LABELS = ["RT6/RNEG2", "SMEG", "RNEG", "NG4", "DISPLAY", "RTx", "CALC MOT", "BSI", 'NISSAN', "AUTRES"]

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueries = Xelon.objects.filter(
            delai_au_en_jours_calendaires__lt=30).exclude(lieu_de_stockage='MAGATTREPA/ZONECE', ilot='LaboQual')
        self.pending = self.pendingQueries.filter(type_de_cloture__in=['', 'Sauvée']).count()
        self.late = self._late_products()
        self.percent = int(self._percent_of_late_products())
        self.listProds = [
            ["RT6/RNEG2", "text-primary"],
            ["SMEG", "text-success"],
            ["RNEG", "text-danger"],
            ["NG4", "text-secondary"],
            ["DISPLAY", "text-dark"],
            ["RTx", "text-info"],
            ["AUTRES", "text-warning"]
        ]

    def _percent_of_late_products(self):
        """
        Calculating the percentage of late products
        :return:
            result
        """
        if self.pending:
            return (self.late / self.pending) * 100
        else:
            return 0

    def _late_products(self):
        """
        Calculating of the number of late products
        :return:
            result
        """
        return self.pendingQueries.filter(delai_au_en_jours_calendaires__gt=3, type_de_cloture='').count()

    def products_count(self):
        """
        Function to count the number of products to repair
        :return:
            list of name and number of different products
        """
        prod_nb, rtx_nb = [], 0
        pending_prod = self.pendingQueries.filter(type_de_cloture__in=['', 'Sauvée'])
        for prod in self.LABELS[:-1]:
            if prod == "RTx":
                for rtx in ["RT3", "RT4", "RT5"]:
                    rtx_nb += pending_prod.filter(modele_produit__startswith=rtx).count()
                prod_nb.append(rtx_nb)
            elif prod in ["CALC MOT", "BSI"]:
                prod_nb.append(pending_prod.filter(famille_produit__startswith=prod).count())
            else:
                prod_nb.append(pending_prod.filter(modele_produit__startswith=prod).count())
        labels_nb = sum(prod_nb)
        prod_nb.append(pending_prod.count() - labels_nb)
        return self.LABELS, prod_nb

    def corvet_count(self):
        """
        Function to count the number of Corvet data
        :return:
            number of Corvet data
        """
        return Corvet.objects.all().count()


class DealAnalysis:
    # LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    LAST_60_DAYS = datetime.datetime.today() - datetime.timedelta(60)

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.queries = Xelon.objects.filter(date_retour__isnull=False)

    def count(self):
        labels, deals_nb = [], []
        deals = Xelon.objects.filter(date_retour__gte=self.LAST_60_DAYS).extra(
            {"day": "date_trunc('day', date_retour)"}).values("day").order_by('date_retour').annotate(count=Count("id"))
        for nb in range(len(deals)):
            labels.append(deals[nb]["day"].strftime("%d/%m/%Y"))
            deals_nb.append(deals[nb]['count'])
        # deals = Xelon.objects.filter(date_retour__gte=self.LAST_60_DAYS).order_by('date_retour')
        # grouped = itertools.groupby(deals, lambda record: record.get('date_retour').strftime("%d/%m/%Y"))
        # deals_by_day = [{'x': day, 'y': len(list(deals_this_day))} for day, deals_this_day in grouped]
        # for day, value in grouped:
        #     labels.append(day)
        #     deals_nb.append(len(list(value)))
        return labels, deals_nb
