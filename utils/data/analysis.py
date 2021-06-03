from django.utils import timezone
# import itertools

from django.db.models.functions import ExtractDay
from django.db.models.aggregates import Count
from django.db.models import Q, F

from squalaetp.models import Xelon, Indicator, ProductCategory
from psa.models import Corvet
from tools.models import Suptech


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
        psa = self._late_filter('PSA')
        clarion = self._late_filter('CLARION')
        etude = self._late_filter('ETUDE')
        autre = self._late_filter('AUTRE')
        calc_mot = self._late_filter('CALCULATEUR')
        defaut = self._late_filter('DEFAUT')
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

    def _late_filter(self, value):
        query_list = [query.product_model for query in ProductCategory.objects.filter(category=value)]
        return self.lateQueryset.filter(modele_produit__in=query_list)


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


class SuptechAnalysis:
    LABELS = ["1 à 2 jours", "3 à 6 jours", "7 jours et plus"]

    def __init__(self):
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        suptechs = Suptech.objects.filter(created_at__isnull=False, modified_at__isnull=False)
        self.total = suptechs.count()
        self.queryset = suptechs.annotate(day_number=day_number).order_by('date')

    def result(self):
        data = {"suptechLabels": self.LABELS, 'suptechValue': []}
        data['suptechValue'].append(self._percent(self.queryset.filter(day_number__lte=2)))
        data['suptechValue'].append(self._percent(self.queryset.filter(day_number__gt=2, day_number__lte=6)))
        data['suptechValue'].append(self._percent(self.queryset.filter(day_number__gt=6)))
        return data

    def _percent(self, queryset):
        if queryset.count() != 0:
            return round(100 * queryset.count() / self.total, 1)
        else:
            return 0
