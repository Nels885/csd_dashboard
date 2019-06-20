from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions

from api.serializers import UserSerializer, GroupSerializer, ProgSerializer, products_count
from squalaetp.models import Xelon


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
        queryset = Xelon.objects.all().prefetch_related('corvet')
        customer_file = self.request.query_params.get('xelon', None)
        if customer_file is not None:
            queryset = Xelon.objects.filter(numero_de_dossier=customer_file).prefetch_related('corvet')
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
