from django.utils.translation import gettext as _
from django.utils import timezone
from django.http.request import QueryDict
from rest_framework.response import Response
from rest_framework import viewsets, permissions, serializers
from rest_framework.filters import SearchFilter, OrderingFilter

from ..serializers import (
    ThermalChamberMeasureSerializer, ThermalChamberMeasureCreateSerializer, BgaTimeSerializer,
    BgaTimeCreateSerializer, RaspiTimeSerializer, RaspiTimeCreateSerializer
)
from prog.serializers import ToolStatusSerializer, ToolLogSerializer
from prog.models import ToolStatus, Log
from tools.models import ThermalChamberMeasure, BgaTime, RaspiTime

from ..utils import TokenAuthSupportQueryString


class ToolStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ToolStatus.objects.all()
    serializer_class = ToolStatusSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    http_method_names = ['get']


class ToolLogViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Log.objects.all()
    serializer_class = ToolLogSerializer
    http_method_names = ['get']


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
        device = self.request.query_params.get("device", "")
        status = self.request.query_params.get("status", "").upper()
        if device and status and status in ['START', 'STOP']:
            data['name'] = device
            serializer = BgaTimeCreateSerializer(data=data)
            try:
                bga_is_active = BgaTime.objects.get(name=device, end_time__isnull=True)
                bga_is_active.save(status=status)
            except BgaTime.DoesNotExist:
                pass
            if status == "START" and serializer.is_valid():
                serializer.save()
            return Response({"response": "OK", "device": device, "status": status})
        return Response({"response": "ERROR"})


class RaspiTimeViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = RaspiTime.objects.all()
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RaspiTimeCreateSerializer
        else:
            return RaspiTimeSerializer

    def create(self, *args, **kwargs):
        data = QueryDict('', mutable=True)
        device = self.request.query_params.get('device', '')
        status = self.request.query_params.get('status', '').upper()
        type_device = self.request.query_params.get('type', '').upper()
        xelon = self.request.query_params.get('xelon', '').upper()
        if device and type_device and status and status in ['START', 'STOP']:
            queryset = RaspiTime.objects.filter(name=device, type=type_device, end_time__isnull=True)
            if not queryset and status == "STOP":
                return Response({"response": "OK", "device": device, "status": "NOT STARTED"})
            for query in queryset:
                query.save(status=status)
            if status == "START":
                data.update({'name': device, 'type': type_device, 'xelon': xelon})
                serializer = RaspiTimeCreateSerializer(data=data)
                if status == "START" and serializer.is_valid():
                    serializer.save()
            return Response({"response": "OK", "device": device, "status": status})
        return Response({"response": "ERROR"})
