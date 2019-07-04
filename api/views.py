from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions


from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, CalSerializer, RaspeediSerializer
from raspeedi.models import Raspeedi
from squalaetp.models import Xelon
from .utils import products_count


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


class CharData(APIView):
    """
    API endpoint that allows chart data to be viewed
    """

    def get(self, request, format=None):
        """
        Return a dictionnary of data
        """
        labels, prod_nb = products_count()
        data = {
            "labels": labels,
            "default": prod_nb,
        }
        return Response(data)
