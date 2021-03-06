import requests

from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import viewsets, permissions, authentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from constance import config

from .serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from .serializers import UnlockSerializer, UnlockUpdateSerializer
from reman.serializers import RemanBatchSerializer, RemanCheckOutSerializer, RemanRepairSerializer, EcuRefBaseSerializer
from raspeedi.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon
from reman.models import Batch, EcuModel, Repair

from .utils import TokenAuthSupportQueryString


def documentation(request):
    """ View of API Documentation page """
    title = "Documentation API"
    card_title = "Documentation"
    domain = config.WEBSITE_DOMAIN
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
    queryset = EcuModel.objects.all().order_by('psa_barcode')
    serializer_class = RemanCheckOutSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['psa_barcode', 'ecu_type__ecu_ref_base__reman_reference']
    http_method_names = ['get']


class RemanRepairViewSet(viewsets.ModelViewSet):
    # authentication_classes = (TokenAuthSupportQueryString,)
    permissions_classes = (permissions.IsAuthenticated,)
    queryset = Repair.objects.all()
    serializer_class = RemanRepairSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'identify_number', 'batch__batch_number', 'psa_barcode', 'batch__ecu_ref_base__ecu_type__hw_reference'
    ]
    http_method_names = ['get']


class RemanEcuRefBaseViewSet(viewsets.ModelViewSet):
    # authentication_classes = (TokenAuthSupportQueryString,)
    permissions_classes = (permissions.IsAuthenticated,)
    queryset = EcuModel.objects.all().order_by('id')
    serializer_class = EcuRefBaseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    http_method_names = ['get']


class NacLicenseView(APIView):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload"
        payload = {
            "mediaVersion": request.GET.get('update'),
            "uin": request.GET.get('uin')
        }
        response = requests.get(url, params=payload, allow_redirects=True)
        if response.status_code == 200:
            return redirect(response.url)
        return Response({"error": "Request failed"}, status=response.status_code)
