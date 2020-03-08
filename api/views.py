from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view

from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from api.serializers import XelonSerializer, CorvetSerializer
from raspeedi.models import Raspeedi
from squalaetp.models import Xelon, Corvet
from utils.data.analysis import ProductAnalysis, DealAnalysis
from api.models import query_xelon_by_args, query_corvet_by_args


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = GroupSerializer


class ProgList(generics.ListAPIView):
    """
    API endpoint that allows prog list to be viewed
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProgSerializer

    def get_queryset(self):
        """
        Provides the list of desired data
        :return:
            Serialized data
        """
        customer_file = self.request.query_params.get('xelon', None)
        vin = self.request.query_params.get('vin', None)
        ref_case = self.request.query_params.get('ref', None)
        if customer_file and vin:
            queryset = Xelon.objects.filter(numero_de_dossier=customer_file, vin=vin).prefetch_related('corvet')
        elif customer_file:
            queryset = Xelon.objects.filter(numero_de_dossier=customer_file).prefetch_related('corvet')
        elif vin:
            queryset = Xelon.objects.filter(vin=vin).prefetch_related('corvet')
        elif ref_case:
            self.serializer_class = RaspeediSerializer
            queryset = Raspeedi.objects.filter(ref_boitier=ref_case)
        else:
            queryset = Xelon.objects.all().prefetch_related('corvet')
        return queryset


class CalList(generics.ListAPIView):
    """
    API endpoint that allows prog list to be viewed
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CalSerializer

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
    queryset = Xelon.objects.all()
    serializer_class = XelonSerializer

    def list(self, request, **kwargs):
        try:
            xelon = query_xelon_by_args(**request.query_params)
            serializer = XelonSerializer(xelon['items'], many=True)
            result = {
                'data': serializer.data,
                'draw': xelon['draw'],
                'recordsTotal': xelon['total'],
                'recordsFiltered': xelon['count']
            }
            return Response(result, status=status.HTTP_200_OK, template_name=None, content_type=None)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)


class CorvetViewSet(viewsets.ModelViewSet):
    queryset = Corvet.objects.all()
    serializer_class = CorvetSerializer

    def list(self, request, **kwargs):
        try:
            corvet = query_corvet_by_args(**request.query_params)
            serializer = CorvetSerializer(corvet['items'], many=True)
            result = {
                'data': serializer.data,
                'draw': corvet['draw'],
                'recordsTotal': corvet['total'],
                'recordsFiltered': corvet['count']
            }
            return Response(result, status=status.HTTP_200_OK, template_name=None, content_type=None)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)


@api_view(['GET'])
def thermal_temp(request):
    data = {'temp': 'Hors ligne'}
    return Response(data, status=status.HTTP_200_OK, template_name=None, content_type=None)
