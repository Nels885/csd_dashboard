from django.utils import timezone
# import itertools

from django.db.models.aggregates import Count
from django.db.models import Q

from squalaetp.models import Xelon, Indicator
from psa.models import Corvet


class ProductAnalysis:
    QUERYSET_RETURN = Xelon.objects.exclude(date_retour__isnull=True)
    QUERYSET = QUERYSET_RETURN.exclude(lieu_de_stockage='ATELIER/AUTOTRONIK')
    QUERYSET_AUTOTRONIK = QUERYSET_RETURN.filter(lieu_de_stockage='ATELIER/AUTOTRONIK')

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueryset = self.QUERYSET.filter(type_de_cloture__in=['', 'Sauvée'])
        self.lateQueryset = self.QUERYSET.filter(Q(delai_au_en_jours_ouvres__gt=3) |
                                                 Q(express=True) |
                                                 Q(famille_produit__startswith='TBORD')).exclude(
            type_de_cloture__in=['Réparé', 'Admin', 'N/A']).order_by('-delai_au_en_jours_ouvres')
        self.pending = self.pendingQueryset.count()
        self.express = self.pendingQueryset.filter(express=True).count()
        self.late = self.lateQueryset.count()
        self.percent = self._percent_of_late_products()

    def _percent_of_late_products(self):
        """
        Calculating the percentage of late products
        :return:
            result
        """
        if self.pending:
            return int((self.late / self.pending) * 100)
        else:
            return 0

    def late_products(self):
        """
        Organization of late products by activity
        :return:
            Dictionary of different activities
        """
        psa = self.lateQueryset.filter(Q(ilot='PSA') |
                                       Q(famille_produit__exact='TBORD PSA')).exclude(famille_produit='CALC MOT')
        clarion = self.lateQueryset.filter(ilot='CLARION')
        etude = self.lateQueryset.filter(ilot='LaboQual').exclude(famille_produit='CALC MOT')
        autre = self.lateQueryset.filter(ilot='ILOTAUTRE').exclude(Q(famille_produit='CALC MOT') |
                                                                   Q(famille_produit__exact='TBORD PSA'))
        calc_mot = self.lateQueryset.filter(famille_produit='CALC MOT')
        defaut = self.lateQueryset.filter(ilot='DEFAUT').exclude(famille_produit='CALC MOT')
        autotronik = self.QUERYSET_AUTOTRONIK.exclude(
            type_de_cloture__in=['Réparé', 'Admin', 'N/A']).order_by('-delai_au_en_jours_ouvres')
        return locals()

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
            self.LAST_60_DAYS = last_query.date_retour - timezone.timedelta(60)
        else:
            self.LAST_60_DAYS = timezone.datetime.today() - timezone.timedelta(60)

    def result(self):
        data = {"areaLabels": [], "prodsInValue": [], "prodsRepValue": [], "prodsExpValue": [], "prodsLateValue": []}
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

    def new_result(self):
        last_60_days = timezone.datetime.today() - timezone.timedelta(60)
        data = {"areaLabels": [], "prodsInValue": [], "prodsRepValue": [], "prodsExpValue": [], "prodsLateValue": []}
        prods = Indicator.objects.filter(date__gte=last_60_days).order_by('date')
        for prod in prods:
            data["areaLabels"].append(prod.date.strftime("%d/%m/%Y"))
            data["prodsInValue"].append(self.queryset.filter(date_retour=prod.date).count())
            data["prodsRepValue"].append(prod.products_to_repair)
            data["prodsExpValue"].append(prod.express_products)
            data["prodsLateValue"].append(prod.late_products)
        return data
