from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from api.serializers import UserSerializer, GroupSerializer, XelonSerializer, CorvetSerializer, products_count
from squalaetp.models import Xelon, Corvet


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class XelonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Xelon.objects.filter(corvet__vin__icontains='vf').prefetch_related('corvet')
    serializer_class = XelonSerializer


class CorvetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Corvet.objects.all()
    serializer_class = CorvetSerializer


class CharData(APIView):

    def get(self, request, format=None):
        labels, prod_nb = products_count()
        data = {
            "labels": labels,
            "default": prod_nb,
        }
        return Response(data)
