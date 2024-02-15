from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from reman.serializers import (
    RemanBatchSerializer, RemanCheckOutSerializer, RemanRepairSerializer, RemanRepairCreateSerializer,
    EcuRefBaseSerializer
)
from reman.models import Batch, EcuModel, Repair, EcuRefBase
from utils.django.validators import validate_barcode

from ..utils import TokenAuthSupportQueryString


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
