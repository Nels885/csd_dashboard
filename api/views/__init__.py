import requests

from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView

from ..serializers import ProgSerializer, CalSerializer
from prog.serializers import UnlockSerializer, UnlockUpdateSerializer, RaspeediSerializer
from prog.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon

from ..utils import TokenAuthSupportQueryString


def documentation(request):
    """ View of API Documentation page """
    title = "Documentation API"
    card_title = "Documentation"
    return render(request, 'api/doc.html', locals())


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
        queryset = Xelon.objects.filter(corvet__isnull=False)
        querystring = self.request.query_params
        if querystring.get('active', 'false') in ['true', 'True']:
            queryset = queryset.filter(is_active=True)
        if querystring.get('prod'):
            queryset = queryset.filter(modele_produit__icontains=querystring.get('prod'))
        if querystring.get('ref'):
            self.serializer_class = RaspeediSerializer
            queryset = Raspeedi.objects.all()
            if querystring.get('ref') != 'all':
                queryset = queryset.filter(ref_boitier=querystring.get('ref'))
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