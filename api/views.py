from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from api.serializers import XelonSerializer, CorvetSerializer
from raspeedi.models import Raspeedi
from squalaetp.models import Xelon, Corvet
from utils.product_Analysis import ProductAnalysis
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


class Charts(APIView):
    """
    API endpoint that allows chart data to be viewed
    """

    def get(self, request, format=None):
        """
        Return a dictionnary of data
        """
        analysis = ProductAnalysis()
        labels, prod_nb = analysis.products_count()
        data = {
            "pieLabels": labels,
            "pieDefault": prod_nb,
            "areaLabels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "areaDefault": [50, 70, 160, 80, 110, 120, 150, 40, 90, 130, 125, 100],
        }
        return Response(data)


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
