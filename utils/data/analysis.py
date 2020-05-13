import datetime
# import itertools

from django.db.models.aggregates import Count
from django.db.models import Q

from squalaetp.models import Xelon, Corvet


class ProductAnalysis:
    LABELS = ["RT6/RNEG2", "SMEG", "NAC", "RNEG", "NG4", "DISPLAY", "RTx", "CALC MOT", "BSI", 'NISSAN', "AUTRES"]

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueries = Xelon.objects.exclude(lieu_de_stockage='MAGATTREPA/ZONECE', ilot='LaboQual')
        self.pending = self.pendingQueries.filter(type_de_cloture__in=['', 'Sauvée']).count()
        self.late = self.late_products().count()
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

    def late_products(self):
        """
        Calculating of the number of late products
        :return:
            result
        """
        return self.pendingQueries.filter(
            delai_au_en_jours_ouvres__gt=3).exclude(type_de_cloture__in=['Réparé', 'Admin'])

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
        return {"prodLabels": self.LABELS, "prodDefault": prod_nb}

    def corvet_count(self):
        """
        Function to count the number of Corvet data
        :return:
            number of Corvet data
        """
        return Corvet.objects.all().count()


class IndicatorAnalysis:

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.queries = Xelon.objects.filter(date_retour__isnull=False)
        last_query = self.queries.order_by('-date_retour').first()
        if last_query:
            self.LAST_60_DAYS = last_query.date_retour - datetime.timedelta(60)
        else:
            self.LAST_60_DAYS = datetime.datetime.today() - datetime.timedelta(60)

    def result(self):
        labels, prods_in_nb, prods_ext_nb = [], [], []
        prods_in = self.queries.filter(date_retour__gte=self.LAST_60_DAYS).extra(
            {"day": "date_trunc('day', date_retour)"}).values("day").order_by('date_retour')
        prods_in = prods_in.annotate(count=Count("id"))
        prods_in = prods_in.annotate(exp=Count("express", filter=Q(express=True)))
        for nb in range(len(prods_in)):
            labels.append(prods_in[nb]["day"].strftime("%d/%m/%Y"))
            prods_in_nb.append(prods_in[nb]["count"])
            prods_ext_nb.append(prods_in[nb]["exp"])
        return {"areaLabels": labels, "prodsInValue": prods_in_nb, "prodsExpValue": prods_ext_nb}
