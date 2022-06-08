import requests

from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import viewsets, permissions, serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView

from .serializers import (
    ProgSerializer, CalSerializer, RaspeediSerializer, UnlockSerializer, UnlockUpdateSerializer,
    ThermalChamberMeasureSerializer, ThermalChamberMeasureCreateSerializer, BgaTimeSerializer, BgaTimeCreateSerializer
)
from reman.serializers import (
    RemanBatchSerializer, RemanCheckOutSerializer, RemanRepairSerializer, RemanRepairCreateSerializer,
    EcuRefBaseSerializer
)
from raspeedi.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon
from reman.models import Batch, EcuModel, Repair, EcuRefBase
from tools.models import ThermalChamberMeasure, BgaTime
from utils.django.validators import validate_barcode

from .utils import TokenAuthSupportQueryString


def documentation(request):
    """ View of API Documentation page """
    title = "Documentation API"
    card_title = "Documentation"
    return render(request, 'api/doc.html', locals())


class UnlockViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UnlockProduct.objects.filter(active=True)
    http_method_names = ['get', 'put']

    def get_queryset(self):
        customer_file = self.request.query_params.get('xelon', None)
        queryset = self.queryset
        if customer_file:
            queryset = UnlockProduct.objects.filter(unlock__numero_de_dossier=customer_file, active=True)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UnlockUpdateSerializer
        else:
            return UnlockSerializer


class ProgViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows prog list to be viewed """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.all()
    serializer_class = ProgSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['numero_de_dossier', 'vin', 'modele_produit']
    http_method_names = ['get']

    def get_queryset(self):
        """
        Provides the list of desired data
        :return:
            Serialized data
        """
        ref_case = self.request.query_params.get('ref', None)
        if ref_case:
            self.serializer_class = RaspeediSerializer
            queryset = Raspeedi.objects.filter(ref_boitier=ref_case)
        else:
            queryset = Xelon.objects.all()
        return queryset


class CalViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows prog list to be viewed """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.all()
    serializer_class = CalSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['numero_de_dossier', 'vin']
    http_method_names = ['get']


class RemanBatchViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Batch.objects.all().order_by('batch_number')
    serializer_class = RemanBatchSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['batch_number', 'ecu_ref_base__reman_reference']
    http_method_names = ['get']


class RemanCheckOutViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = EcuModel.objects.all().order_by('barcode')
    serializer_class = RemanCheckOutSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['barcode', 'ecu_type__ecurefbase__reman_reference', 'ecu_type__hw_reference']
    http_method_names = ['get']


class RemanRepairViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Repair.objects.all()
    serializer_class = RemanRepairSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'identify_number', 'batch__batch_number', 'barcode', 'batch__ecu_ref_base__ecu_type__hw_reference'
    ]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RemanRepairCreateSerializer
        else:
            return RemanRepairSerializer

    def create(self, *args, **kwargs):
        data = self.request.data
        identify_number, barcode = data.get("identify_number"), data.get("barcode")
        vin, diagnostic_data = data.get("vin", ""), data.get("diagnostic_data", "")
        if identify_number and barcode:
            batch_number = identify_number[:-3] + "000"
            code, batch_type = validate_barcode(barcode)
            try:
                Batch.objects.get(
                    batch_number__startswith=batch_number, ecu_ref_base__ecu_type__ecumodel__barcode__exact=code)
                Repair.objects.update_or_create(
                    identify_number=identify_number, barcode=barcode, defaults={
                        'vin': vin, 'diagnostic_data': diagnostic_data
                    }
                )
                return Response({"response": "OK", "data": data})
            except (Batch.DoesNotExist, Batch.MultipleObjectsReturned, IntegrityError):
                return Response({"response": "barcode is invalid"})
        return Response({"response": "ERROR"})


class RemanEcuRefBaseViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = EcuRefBase.objects.all().order_by('id')
    serializer_class = EcuRefBaseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    http_method_names = ['get']


class NacLicenseView(APIView):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        if request.GET.get('update') and request.GET.get('uin'):
            url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload"
            payload = {
                "mediaVersion": request.GET.get('update'),
                "uin": request.GET.get('uin')
            }
            response = requests.get(url, params=payload, allow_redirects=True)
            if response.status_code == 200:
                return redirect(response.url)
        return Response({"error": "Request failed"}, status=404)


class ThermalChamberMeasureViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ThermalChamberMeasure.objects.all()
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ThermalChamberMeasureCreateSerializer
        else:
            return ThermalChamberMeasureSerializer

    def create(self, *args, **kwargs):
        data = self.request.data
        if self.request.query_params.get('value', None):
            data['value'] = self.request.query_params.get('value', None)
        serializer = ThermalChamberMeasureCreateSerializer(data=data)
        if serializer.is_valid():
            measure = ThermalChamberMeasure.objects.order_by('datetime').last()
            if not measure or (timezone.now() - measure.datetime).seconds >= (10 * 60):
                serializer.save()
                return Response(serializer.data)
            raise serializers.ValidationError({'warning': _('Time between 2 requests too short')})
        return Response(serializer.errors)


class BgaTimeViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BgaTime.objects.all()
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BgaTimeCreateSerializer
        else:
            return BgaTimeSerializer

    def create(self, *args, **kwargs):
        data = self.request.data
        device = self.request.query_params.get("device", None)
        status = self.request.query_params.get("status", None)
        if device and status:
            data['name'] = device
            serializer = BgaTimeCreateSerializer(data=data)
            try:
                bga_is_active = BgaTime.objects.get(name=device, end_time__isnull=True)
                bga_is_active.save(status=status)
            except BgaTime.DoesNotExist:
                pass
            if status.upper() == "START" and serializer.is_valid():
                serializer.save()
            return Response({"response": "OK", "device": device, "status": status.upper()})
        return Response({"response": "ERROR"})
