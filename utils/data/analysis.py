from django.utils import timezone
# import itertools

from django.db.models.functions import ExtractDay, TruncDay, TruncMonth
from django.db.models.aggregates import Count, Sum
from django.db.models import Q, F, Case, When, IntegerField

from squalaetp.models import Xelon, Indicator
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
                                                 Q(express=True)).exclude(
            type_de_cloture__in=['Réparé', 'Admin', 'N/A']).order_by('-delai_au_en_jours_ouvres')
        self.pending = self.pendingQueryset.count()
        self.express = self.pendingQueryset.filter(express=True).count()
        self.vip = self.pendingQueryset.filter(dossier_vip=True).count()
        self.admin = self.QUERYSET.filter(type_de_cloture='Admin').count()
        self.sp = self.QUERYSET.filter(type_de_cloture='Att SP').count()
        self.ecu = self.pendingQueryset.filter(product__category='CALCULATEUR').count()
        self.media = self.pendingQueryset.exclude(product__category='CALCULATEUR').count()
        self.late = self.lateQueryset.count()
        self.tronik = self.QUERYSET_AUTOTRONIK.exclude(type_de_cloture__in=['Réparé', 'Admin', 'N/A']).count()
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
        psa = self.lateQueryset.filter(product__category='PSA')
        clarion = self.lateQueryset.filter(product__category='CLARION')
        etude = self.lateQueryset.filter(product__category='ETUDE')
        autre = self.lateQueryset.filter(product__category='AUTRE')
        calc_mot = self.lateQueryset.filter(product__category='CALCULATEUR')
        defaut = self.lateQueryset.filter(product__category='DEFAUT')
        return locals()

    def admin_products(self):
        queryset = self.QUERYSET.filter(type_de_cloture='Admin').order_by('-delai_au_en_jours_ouvres')
        return locals()

    def vip_products(self):
        queryset = self.pendingQueryset.filter(dossier_vip=True).order_by('-delai_au_en_jours_ouvres')
        return locals()

    def autotronik(self):
        autotronik = self.QUERYSET_AUTOTRONIK.exclude(
            type_de_cloture__in=['Réparé', 'Admin', 'N/A']).order_by('-delai_au_en_jours_ouvres')
        return locals()

    @staticmethod
    def corvet_count():
        """
        Function to count the number of Corvet data
        :return:
            number of Corvet data
        """
        return Corvet.objects.all().count()

    @staticmethod
    def xelon_count():
        """
        Function to count the number of Xelon data
        :return:
            number of Xelon data
        """
        return Xelon.objects.all().count()


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
    SUPTECH_CO_LABELS = ["En Attente", "En Cours", "Cloturée", "Annulée"]
    BGA = {"bgaOneValue": "DES-48", "bgaTwoValue": "DES-51"}
    LAST_60_DAYS = timezone.datetime.today() - timezone.timedelta(60)
    LAST_30_DAYS = timezone.datetime.today() - timezone.timedelta(30)
    TOTAL_HOURS = 7 * 60 * 60

    def __init__(self):
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        suptechs = Suptech.objects.filter(created_at__isnull=False, modified_at__isnull=False)
        self.suptechs = suptechs.annotate(day_number=day_number).order_by('date')
        self.bgaTimes = BgaTime.objects.filter(date__gte=self.LAST_60_DAYS)
        self.tcMeasure = ThermalChamberMeasure.objects.filter(datetime__isnull=False).order_by('datetime')

    def suptech_co(self):
        suptechs = Suptech.objects.filter(category=3)
        total = suptechs.count()
        data = {"suptechCoLabels": self.SUPTECH_CO_LABELS, 'suptechCoValue': []}
        data['suptechCoValue'].append(self._percent(suptechs.filter(status="En Attente").count(), total))
        data['suptechCoValue'].append(self._percent(suptechs.filter(status="En Cours").count(), total))
        data['suptechCoValue'].append(self._percent(suptechs.filter(status="Cloturée").count(), total))
        data['suptechCoValue'].append(self._percent(suptechs.filter(status="Annulée").count(), total))
        return data

    def suptech_ce(self):
        suptechs = self.suptechs.exclude(category=3)
        data = {"suptechCeLabels": [], "twoDays": [], "twoToSixDays": [], "sixDays": []}
        queryset = self._suptech_annotate(suptechs)
        for query in queryset:
            data["suptechCeLabels"].append(query['month'].strftime("%m/%Y"))
            data["twoDays"].append(self._percent(query['two_days'], query['total']))
            data["twoToSixDays"].append(self._percent(query['two_to_six_days'], query['total']))
            data["sixDays"].append(self._percent(query['six_days'], query['total']))
        return data

    def bga_time(self):
        total = self.TOTAL_HOURS
        data = {"bgaAreaLabels": [], "bgaTotalValue": [], "bgaOneValue": [], "bgaTwoValue": []}
        queryset = self._bga_annotate(self.bgaTimes)
        for query in queryset:
            data["bgaAreaLabels"].append(query['sum_date'].strftime("%d/%m/%Y"))
            data["bgaTotalValue"].append(self._percent(query['sum_duration'], total))
            data["bgaOneValue"].append(self._percent(query['sum_bga_one'], total))
            data["bgaTwoValue"].append(self._percent(query['sum_bga_two'], total))
        return data

    def thermal_chamber_measure(self):
        data = {"tcAreaLabels": [], "tcTempValue": []}
        if self.tcMeasure:
            for query in self.tcMeasure.filter(datetime__gte=self.LAST_30_DAYS):
                data["tcAreaLabels"].append(timezone.localtime(query.datetime).strftime("%d/%m/%Y %H:%M"))
                data["tcTempValue"].append(query.temp[:-2])
        return data

    def all(self):
        return dict(**self.suptech_ce(), **self.suptech_co(), **self.bga_time(), **self.thermal_chamber_measure())

    @staticmethod
    def _percent(value, total=None, total_multiplier=1):
        if isinstance(total, int) and total != 0 and isinstance(value, int) and value != 0:
            return round(100 * value / (total * total_multiplier), 1)
        else:
            return 0

    @staticmethod
    def _bga_annotate(queryset):
        queryset = queryset.annotate(sum_date=TruncDay("date")).values("sum_date").order_by("sum_date")
        queryset = queryset.annotate(
            sum_bga_one=Sum(Case(When(name='DES-48', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_bga_two=Sum(Case(When(name='DES-51', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(sum_duration=Sum('duration'))
        return queryset

    @staticmethod
    def _suptech_annotate(queryset):
        queryset = queryset.annotate(month=TruncMonth("date")).values("month").order_by("month")
        queryset = queryset.annotate(total=Count("month"))
        queryset = queryset.annotate(two_days=Count("day_number", filter=Q(day_number__lte=2)))
        queryset = queryset.annotate(two_to_six_days=Count("day_number", filter=Q(day_number__gt=2, day_number__lte=6)))
        queryset = queryset.annotate(six_days=Count("day_number", filter=Q(day_number__gt=6)))
        return queryset
