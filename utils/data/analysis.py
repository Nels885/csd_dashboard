import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
# import itertools

from django.db.models.functions import ExtractDay, TruncDay, TruncMonth, Concat
from django.db.models.aggregates import Count, Sum
from django.db.models import Q, F, Case, When, IntegerField, CharField, Value as V

from squalaetp.models import Xelon, Indicator
from psa.models import Corvet
from tools.models import Suptech, BgaTime, ThermalChamberMeasure, RaspiTime


class ProductAnalysis:
    QUERYSET_RETURN = Xelon.objects.exclude(date_retour__isnull=True).order_by('date_expedition_attendue')
    QUERYSET = QUERYSET_RETURN.exclude(lieu_de_stockage='ATELIER/AUTOTRONIK')
    QUERYSET_AUTOTRONIK = QUERYSET_RETURN.filter(lieu_de_stockage='ATELIER/AUTOTRONIK')

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueryset = self.QUERYSET.exclude(type_de_cloture__in=['Réparé', 'N/A', 'Rebut'])
        self.lateQueryset = self.QUERYSET.filter(Q(delai_expedition_attendue__gt=0) | Q(express=True)).exclude(
            type_de_cloture__in=['Réparé', 'Admin', 'N/A', 'Rebut'])
        self.pending = self.pendingQueryset.count()
        self.express = self.pendingQueryset.filter(express=True).count()
        self.vip = self.pendingQueryset.filter(dossier_vip=True).count()
        self.admin = self.QUERYSET.filter(type_de_cloture='Admin').count()
        self.sp = self.QUERYSET.filter(type_de_cloture='Att SP').count()
        self.ecu = self.pendingQueryset.filter(product__category='CALCULATEUR').count()
        self.media = self.pendingQueryset.exclude(product__category='CALCULATEUR').count()
        self.late = self.lateQueryset.count()
        self.tronik = self.QUERYSET_AUTOTRONIK.exclude(type_de_cloture__in=['Réparé', 'Admin', 'N/A', 'Rebut']).count()
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
        return self._activity_dict(self.lateQueryset)

    def pending_products(self):
        """
        Organization of pending products by activity
        :return:
            Dictionary of different activities
        """
        return self._activity_dict(self.pendingQueryset)

    def admin_products(self):
        queryset = self._mailto_annotate(self.QUERYSET.filter(type_de_cloture='Admin'))
        return locals()

    def vip_products(self):
        queryset = self._mailto_annotate(self.pendingQueryset.filter(dossier_vip=True))
        return locals()

    def autotronik(self):
        autotronik = self.QUERYSET_AUTOTRONIK.exclude(type_de_cloture__in=['Réparé', 'Admin', 'N/A', 'Rebut'])
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

    def _activity_dict(self, queryset):
        queryset = self._mailto_annotate(queryset)
        psa = queryset.filter(product__category='PSA')
        clarion = queryset.filter(product__category='CLARION')
        etude = queryset.filter(product__category='ETUDE')
        autre = queryset.filter(product__category='AUTRE')
        calc_mot = queryset.filter(product__category='CALCULATEUR')
        defaut = queryset.filter(product__category='DEFAUT')
        return locals()

    @staticmethod
    def _mailto_annotate(queryset):
        return queryset.annotate(
            subject=Concat('numero_de_dossier', V(' - '), 'modele_produit', output_field=CharField())
        )


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
        data = {"prodsAreaLabels": [], "prodsInValue": [], "prodsRepValue": [], "prodsExpValue": [],
                "prodsLateValue": []}
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
    LAST_12_MONTHS = timezone.datetime.today() + relativedelta(months=-12)
    TOTAL_HOURS = 7 * 60 * 60

    def __init__(self):
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        # suptechs = Suptech.objects.filter(created_at__isnull=False, modified_at__isnull=False)
        suptechs = Suptech.objects.filter(
            created_at__isnull=False, modified_at__isnull=False, date__gte=self.LAST_12_MONTHS)
        self.suptechs = suptechs.annotate(day_number=day_number).order_by('date')
        self.bgaTimes = BgaTime.objects.filter(date__gte=self.LAST_60_DAYS)
        self.raspiTimes = RaspiTime.objects.filter(date__gte=self.LAST_60_DAYS)
        self.tcMeasure = ThermalChamberMeasure.objects.filter(datetime__isnull=False).order_by('datetime')

    def suptech_co(self):
        suptechs = self.suptechs.filter(category__name__icontains="operation")
        suptechs_old = suptechs.filter(date__lt=datetime.date(2024, 1, 1))
        suptechs_old = self._suptech_old_annotate(suptechs_old)
        suptechs_new = suptechs.filter(date__gte=datetime.date(2024, 1, 1))
        suptechs_new = self._suptech_annotate(suptechs_new)
        data = {
            "suptechCoLabels": [], "coTwoDays": [], "coTwoToSixDays": [], "coSixDays": [], "coExpRate": [],
            "coSupNumber": []
        }
        queryset = suptechs_old | suptechs_new
        for query in queryset:
            data["suptechCoLabels"].append(query['month'].strftime("%m/%Y"))
            data["coTwoDays"].append(self._percent(query['two_days'], query['total_48h'], default=100))
            data["coTwoToSixDays"].append(self._percent(query['two_to_six_days'], query['total_48h']))
            data["coSixDays"].append(self._percent(query['six_days'], query['total_48h']))
            data["coExpRate"].append(self._percent(query['total_48h'], query['total']))
            data["coSupNumber"].append(query['total'])
        return data

    def suptech_ce(self):
        suptechs_old = self.suptechs.exclude(category=3).filter(date__lt=datetime.date(2024, 1, 1))
        suptechs_old = self._suptech_old_annotate(suptechs_old)
        suptechs_new = self.suptechs.filter(category__name__icontains="etude", date__gte=datetime.date(2024, 1, 1))
        suptechs_new = self._suptech_annotate(suptechs_new)
        data = {
            "suptechCeLabels": [], "twoDays": [], "twoToSixDays": [], "sixDays": [], "expRate": [], "supNumber": []
        }
        queryset = suptechs_old | suptechs_new
        for query in queryset:
            data["suptechCeLabels"].append(query['month'].strftime("%m/%Y"))
            data["twoDays"].append(self._percent(query['two_days'], query['total_48h'], default=100))
            data["twoToSixDays"].append(self._percent(query['two_to_six_days'], query['total_48h']))
            data["sixDays"].append(self._percent(query['six_days'], query['total_48h']))
            data["expRate"].append(self._percent(query['total_48h'], query['total']))
            data["supNumber"].append(query['total'])
        return data

    def bga_time(self):
        total = self.TOTAL_HOURS
        data = {"bgaAreaLabels": [], "bgaTotalValue": [], "bgaOneValue": [], "bgaTwoValue": []}
        queryset = self._bga_annotate(self.bgaTimes)
        for query in queryset:
            data["bgaAreaLabels"].append(query['sum_date'].strftime("%d/%m/%Y"))
            data["bgaTotalValue"].append(self._percent(query['sum_duration'], total, 2))
            data["bgaOneValue"].append(self._percent(query['sum_one'], total))
            data["bgaTwoValue"].append(self._percent(query['sum_two'], total))
        return data

    def raspi_time(self):
        total = self.TOTAL_HOURS
        data = {
            "raspiAreaLabels": [], "raspiTotalValue": [], "raspiOneValue": [], "raspiTwoValue": [],
            "raspiThreeValue": [], "raspiFourValue": [], "raspiFiveValue": [], "raspiSevenValue": [],
            "raspiEightValue": [], "raspiNineValue": []
        }
        queryset = self._raspi_annotate(self.raspiTimes)
        for query in queryset:
            data["raspiAreaLabels"].append(query['sum_date'].strftime("%d/%m/%Y"))
            data["raspiTotalValue"].append(self._percent(query['sum_duration'], total, 8))
            data["raspiOneValue"].append(self._percent(query['sum_one'], total))
            data["raspiTwoValue"].append(self._percent(query['sum_two'], total))
            data["raspiThreeValue"].append(self._percent(query['sum_three'], total))
            data["raspiFourValue"].append(self._percent(query['sum_four'], total))
            data["raspiFiveValue"].append(self._percent(query['sum_five'], total))
            data["raspiSevenValue"].append(self._percent(query['sum_seven'], total))
            data["raspiEightValue"].append(self._percent(query['sum_eight'], total))
            data["raspiNineValue"].append(self._percent(query['sum_nine'], total))
        return data

    def thermal_chamber_measure(self):
        data = {"tcAreaLabels": [], "tcTempValue": []}
        if self.tcMeasure:
            for query in self.tcMeasure.filter(datetime__gte=self.LAST_30_DAYS):
                data["tcAreaLabels"].append(timezone.localtime(query.datetime).strftime("%d/%m/%Y %H:%M"))
                data["tcTempValue"].append(query.temp[:-2])
        return data

    def all(self):
        return dict(
            **self.suptech_ce(), **self.suptech_co(), **self.bga_time(), **self.raspi_time(),
            **self.thermal_chamber_measure()
        )

    def suptech(self):
        return dict(**self.suptech_ce(), **self.suptech_co())

    def use_tools(self):
        return dict(**self.bga_time(), **self.raspi_time(), **self.thermal_chamber_measure())

    @staticmethod
    def _percent(value, total=None, total_multiplier=1, default=0):
        if isinstance(total, int) and total != 0 and isinstance(value, int) and value != 0:
            result = round(100 * value / (total * total_multiplier), 1)
            if result <= 100:
                return result
        return default

    @staticmethod
    def _bga_annotate(queryset):
        queryset = queryset.annotate(sum_date=TruncDay("date")).values("sum_date").order_by("sum_date")
        queryset = queryset.annotate(
            sum_one=Sum(Case(When(name='DES-48', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_two=Sum(Case(When(name='DES-51', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(sum_duration=Sum('duration'))
        return queryset

    @staticmethod
    def _raspi_annotate(queryset):
        queryset = queryset.annotate(sum_date=TruncDay("date")).values("sum_date").order_by("sum_date")
        queryset = queryset.annotate(
            sum_one=Sum(Case(When(name='Raspeedi1', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_two=Sum(Case(When(name='Raspeedi2', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_three=Sum(Case(When(name='Raspeedi3', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_four=Sum(Case(When(name='Raspeedi4', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_five=Sum(Case(When(name='Raspeedi5', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_seven=Sum(Case(When(name='Raspeedi7', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_eight=Sum(Case(When(name='Raspeedi8', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(
            sum_nine=Sum(Case(When(name='Raspeedi9', then=F('duration')), output_field=IntegerField(), default=0)))
        queryset = queryset.annotate(sum_duration=Sum('duration'))
        return queryset

    @staticmethod
    def _suptech_old_annotate(queryset):
        queryset = queryset.annotate(month=TruncMonth("created_at")).values("month").order_by("month")
        queryset = queryset.annotate(total=Count("month"))
        queryset = queryset.annotate(total_48h=Count("month", filter=Q(is_48h=True)))
        queryset = queryset.annotate(two_days=Count("month", filter=Q(day_number__lte=2, is_48h=True)))
        queryset = queryset.annotate(
            two_to_six_days=Count("month", filter=Q(day_number__gt=2, day_number__lte=6, is_48h=True)))
        queryset = queryset.annotate(six_days=Count("month", filter=Q(day_number__gt=6, is_48h=True)))
        return queryset

    @staticmethod
    def _suptech_annotate(queryset):
        queryset = queryset.annotate(month=TruncMonth("created_at")).values("month").order_by("month")
        queryset = queryset.annotate(total=Count("month"))
        queryset = queryset.annotate(total_48h=Count("month", filter=Q(is_48h=True)))
        queryset = queryset.annotate(two_days=Count("month", filter=Q(days_late__lte=2, is_48h=True)))
        queryset = queryset.annotate(
            two_to_six_days=Count("month", filter=Q(day_number__gt=2, days_late__lte=6, is_48h=True)))
        queryset = queryset.annotate(six_days=Count("month", filter=Q(days_late__gt=6, is_48h=True)))
        return queryset
