from django.contrib.auth.models import User, Group
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status, authentication
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from api.serializers import XelonSerializer, CorvetSerializer, UnlockSerializer, UnlockUpdateSerializer
from raspeedi.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon, Corvet
from tools.models import ThermalChamber
from utils.data.analysis import ProductAnalysis, IndicatorAnalysis
from api.models import (query_table_by_args,
                        ORDER_CORVET_COLUMN_CHOICES, ORDER_XELON_COLUMN_CHOICES,
                        xelon_filter, corvet_filter)

from utils.data.mqtt import MQTT_CLIENT
from .utils import TokenAuthSupportQueryString


def documentation(request):
    """ View of API Documentation page """
    title = "Documentation API"
    card_title = "Documentation"
    return render(request, 'api/doc.html', locals())


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


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
            queryset = UnlockProduct.objects.filter(unlock__numero_de_dossier=customer_file)
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
    queryset = Xelon.objects.all().prefetch_related('corvet')
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
            queryset = Xelon.objects.all().prefetch_related('corvet')
        return queryset


class CalViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows prog list to be viewed """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.all().prefetch_related('corvet')
    serializer_class = CalSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['numero_de_dossier', 'vin']
    http_method_names = ['get']


@api_view(['GET'])
def charts(request):
    """
    API endpoint that allows chart data to be viewed
    """
    analysis, indicator = ProductAnalysis(), IndicatorAnalysis()
    data = analysis.products_count()
    data.update(indicator.result())
    return Response(data, status=status.HTTP_200_OK)


class XelonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.filter(date_retour__isnull=False)
    serializer_class = XelonSerializer

    def list(self, request, **kwargs):
        try:
            folder = self.request.query_params.get('folder', None)
            if folder and folder == 'pending':
                self.queryset = self.queryset.exclude(type_de_cloture='Réparé')
            xelon = query_table_by_args(xelon_filter, self.queryset, ORDER_XELON_COLUMN_CHOICES, **request.query_params)
            serializer = XelonSerializer(xelon["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": xelon["draw"],
                "recordsTotal": xelon["total"],
                "recordsFiltered": xelon["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


class CorvetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Corvet.objects.all()
    serializer_class = CorvetSerializer

    def list(self, request, **kwargs):
        try:
            corvet = query_table_by_args(corvet_filter, self.queryset, ORDER_CORVET_COLUMN_CHOICES,
                                         **request.query_params)
            serializer = CorvetSerializer(corvet["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": corvet["draw"],
                "recordsTotal": corvet["total"],
                "recordsFiltered": corvet["count"]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def thermal_temp(request):
    data = MQTT_CLIENT.result()
    now = timezone.now()
    if "Hors ligne" not in data["temp"]:
        if float(data['temp'][:-2]) < -10:
            thermals = ThermalChamber.objects.filter(operating_mode='FROID', active=True, start_time__isnull=True)
            thermals.update(start_time=now)
        elif float(data['temp'][:-2]) > 40:
            thermals = ThermalChamber.objects.filter(operating_mode='CHAUD', active=True, start_time__isnull=True)
            thermals.update(start_time=now)
    return Response(data, status=status.HTTP_200_OK, template_name=None, content_type=None)
