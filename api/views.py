from django.contrib.auth.models import User, Group
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status, authentication
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter

from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from api.serializers import XelonSerializer, CorvetSerializer, UnlockSerializer, UnlockUpdateSerializer
from raspeedi.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon, Corvet
from utils.data.analysis import ProductAnalysis, DealAnalysis
from api.models import (query_table_by_args,
                        ORDER_CORVET_COLUMN_CHOICES, ORDER_XELON_COLUMN_CHOICES,
                        xelon_filter, corvet_filter)

from utils.data import mqtt
from .utils import TokenAuthSupportQueryString


def documentation(request):
    """
    View of API Documentation page
    """
    context = {
        'title': "Documentation API",
        'card_title': 'Documentation'
    }
    return render(request, 'api/api_documentation.html', context)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class UnlockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
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
    """
    API endpoint that allows prog list to be viewed
    """
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
        # customer_file = self.request.query_params.get('xelon', None)
        # vin = self.request.query_params.get('vin', None)
        ref_case = self.request.query_params.get('ref', None)
        # if customer_file and vin:
        #     queryset = Xelon.objects.filter(numero_de_dossier=customer_file, vin=vin).prefetch_related('corvet')
        # elif customer_file:
        #     queryset = Xelon.objects.filter(numero_de_dossier=customer_file).prefetch_related('corvet')
        # elif vin:
        #     queryset = Xelon.objects.filter(vin=vin).prefetch_related('corvet')
        if ref_case:
            self.serializer_class = RaspeediSerializer
            queryset = Raspeedi.objects.filter(ref_boitier=ref_case)
        else:
            queryset = Xelon.objects.all().prefetch_related('corvet')
        return queryset


class CalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows prog list to be viewed
    """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.all().prefetch_related('corvet')
    serializer_class = CalSerializer
    http_method_names = ['get']

    def get_queryset(self):
        """
        Provides the list of desired data
        :return:
            Serialized data
        """
        customer_file = self.request.query_params.get('xelon', None)
        vin = self.request.query_params.get('vin', None)
        if customer_file and vin:
            queryset = Xelon.objects.filter(numero_de_dossier=customer_file, vin=vin).prefetch_related('corvet')
        elif customer_file:
            queryset = Xelon.objects.filter(numero_de_dossier=customer_file).prefetch_related('corvet')
        elif vin:
            queryset = Xelon.objects.filter(vin=vin).prefetch_related('corvet')
        else:
            queryset = Xelon.objects.all().prefetch_related('corvet')
        return queryset


@api_view(['GET'])
def charts(request):
    """
    API endpoint that allows chart data to be viewed
    """
    analysis, deal = ProductAnalysis(), DealAnalysis()
    prod_labels, prod_nb = analysis.products_count()
    deal_labels, deal_nb = deal.count()
    data = {
        "prodLabels": prod_labels,
        "prodDefault": prod_nb,
        "dealLabels": deal_labels,
        "dealDefault": deal_nb,
    }
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
    if not mqtt.error:
        mqtt.client.loop_start()
    data = mqtt.payload
    return Response(data, status=status.HTTP_200_OK, template_name=None, content_type=None)
