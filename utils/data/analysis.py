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
        self.queryset = Xelon.objects.exclude(lieu_de_stockage='MAGATTREPA/ZONECE', ilot='LaboQual')
        self.pendingQueryset = self.queryset.filter(type_de_cloture__in=['', 'Sauvée'])
        self.pending = self.pendingQueryset.count()
        self.express = self.pendingQueryset.filter(express=True).count()
        self.late = self.late_products().count()
        self.percent = int(self._percent_of_late_products())

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
        return self.queryset.filter(delai_au_en_jours_ouvres__gt=3).exclude(type_de_cloture__in=['Réparé', 'Admin'])

    def products_count(self):
        """
        Function to count the number of products to repair
        :return:
            list of name and number of different products
        """
        prod_nb, rtx_nb = [], 0
        pending_prod = self.pendingQueryset
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
        self.queryset = Xelon.objects.filter(date_retour__isnull=False)
        last_query = self.queryset.order_by('-date_retour').first()
        if last_query:
            self.LAST_60_DAYS = last_query.date_retour - datetime.timedelta(60)
        else:
            self.LAST_60_DAYS = datetime.datetime.today() - datetime.timedelta(60)

    def result(self):
        data = {"areaLabels": [], "prodsInValue": [], "prodsExpValue": [], "prodsLateValue": []}
        prods_in = self.queryset.filter(date_retour__gte=self.LAST_60_DAYS).extra(
            {"day": "date_trunc('day', date_retour)"}).values("day").order_by('date_retour')
        prods_in = prods_in.annotate(count=Count("id"))
        prods_in = prods_in.annotate(exp=Count("express", filter=Q(express=True)))
        prods_in = prods_in.annotate(late=Count("delai_au_en_jours_ouvres", filter=Q(delai_au_en_jours_ouvres__gt=3)))
        for nb in range(len(prods_in)):
            data["areaLabels"].append(prods_in[nb]["day"].strftime("%d/%m/%Y"))
            data["prodsInValue"].append(prods_in[nb]["count"])
            data["prodsExpValue"].append(prods_in[nb]["exp"])
            data["prodsLateValue"].append(prods_in[nb]["late"])
        return data
