from django.utils import timezone
# import itertools

from django.db.models.functions import ExtractDay, TruncDay
from django.db.models.aggregates import Count, Sum
from django.db.models import Q, F

from squalaetp.models import Xelon, Indicator, ProductCategory
from psa.models import Corvet
from tools.models import Suptech, BgaTime, ThermalChamberMeasure


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
        data = {"prodsAreaLabels": [], "prodsInValue": [], "prodsRepValue": [], "prodsExpValue": [], "prodsLateValue": []}
        prods = Indicator.objects.filter(date__gte=last_60_days).order_by('date')
        for prod in prods:
            data["prodsAreaLabels"].append(prod.date.strftime("%d/%m/%Y"))
            data["prodsInValue"].append(self.queryset.filter(date_retour=prod.date).count())
            data["prodsRepValue"].append(prod.products_to_repair)
            data["prodsExpValue"].append(prod.express_products)
            data["prodsLateValue"].append(prod.late_products)
        return data


class ToolsAnalysis:
    SUPTECH_LABELS = ["1 à 2 jours", "3 à 6 jours", "7 jours et plus"]
    BGA = {"bgaOneValue": "DES-48", "bgaTwoValue": "DES-51"}
    TOTAL_HOURS = 7 * 60 * 60

    def __init__(self):
        last_60_days = timezone.datetime.today() - timezone.timedelta(60)
        last_30_days = timezone.datetime.today() - timezone.timedelta(30)
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        suptechs = Suptech.objects.filter(created_at__isnull=False, modified_at__isnull=False)
        self.suptechs = suptechs.annotate(day_number=day_number).order_by('date')
        self.bgaTimes = BgaTime.objects.filter(date__gte=last_60_days)
        self.tcMeasure = ThermalChamberMeasure.objects.filter(datetime__gte=last_30_days).order_by('datetime')
        self.total = None

    def suptech(self):
        self.total = self.suptechs.count()
        data = {"suptechLabels": self.SUPTECH_LABELS, 'suptechValue': []}
        data['suptechValue'].append(self._percent(self.suptechs.filter(day_number__lte=2).count()))
        data['suptechValue'].append(self._percent(self.suptechs.filter(day_number__gt=2, day_number__lte=6).count()))
        data['suptechValue'].append(self._percent(self.suptechs.filter(day_number__gt=6).count()))
        return data

    def bga_time(self):
        self.total = self.TOTAL_HOURS
        data = {"bgaAreaLabels": [], "bgaTotalValue": [], "bgaOneValue": [], "bgaTwoValue": []}
        queryset = self._bga_annotate(self.bgaTimes)
        for query in queryset:
            data["bgaAreaLabels"].append(query['sum_date'].strftime("%d/%m/%Y"))
            data["bgaTotalValue"].append(self._percent(query['sum_duration'], 2))
        for key, value in self.BGA.items():
            queryset = self._bga_annotate(self.bgaTimes.filter(name=value))
            for query in queryset:
                data[key].append(self._percent(query['sum_duration']))
        return data

    def thermal_chamber_measure(self):
        data = {"tcAreaLabels": [], "tcTempValue": []}
        for query in self.tcMeasure:
            data["tcAreaLabels"].append(query.datetime.strftime("%d/%m/%Y %H:%M"))
            data["tcTempValue"].append(query.temp[:-2])
        return data

    def _percent(self, value, total_multiplier=1):
        if self.total and value != 0:
            return round(100 * value / (self.total * total_multiplier), 1)
        else:
            return 0

    @staticmethod
    def _bga_annotate(queryset):
        return queryset.annotate(
            sum_date=TruncDay("date")).values("sum_date").annotate(sum_duration=Sum('duration')).order_by("sum_date")
