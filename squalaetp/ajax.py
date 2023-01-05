from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from .serializers import (
    XelonSerializer, XELON_COLUMN_LIST, XelonTemporarySerializer, XELON_TEMP_COLUMN_LIST,
    SivinSerializer, SIVIN_COLUMN_LIST, SparePartSerializer, SPAREPART_COLUMN_LIST
)
from .models import Xelon, XelonTemporary, SparePart, Sivin

from utils.django.datatables import QueryTableByArgs
from utils.django.validators import VIN_OLD_PSA_REGEX


class XelonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.filter(date_retour__isnull=False)
    serializer_class = XelonSerializer

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            xelon = QueryTableByArgs(self.queryset, XELON_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(xelon["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": xelon["draw"],
                "recordsTotal": xelon["total"],
                "recordsFiltered": xelon["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query and query == 'pending':
            self.queryset = self.queryset.exclude(type_de_cloture__in=['Réparé', 'N/A', 'Rebut'])
        elif query and query == "vin-error":
            self.queryset = self.queryset.filter(vin_error=True).order_by('-date_retour')
        elif query and query == "corvet-error":
            self.queryset = self.queryset.filter(
                vin__regex=VIN_OLD_PSA_REGEX, vin_error=False, corvet__isnull=True).order_by('-date_retour')
        elif query:
            self.queryset = Xelon.search(query)


class TemporaryViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = XelonTemporary.objects.all()
    serializer_class = XelonTemporarySerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset, XELON_TEMP_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


class StockViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset, SPAREPART_COLUMN_LIST, 0, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


class SivinViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Sivin.objects.all()
    serializer_class = SivinSerializer

    def list(self, request, **kwargs):
        try:
            sivin = QueryTableByArgs(self.queryset, SIVIN_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(sivin["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": sivin["draw"],
                "recordsTotal": sivin["total"],
                "recordsFiltered": sivin["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


def xelon_prod_ajax(request):
    data = {"prod": ""}
    try:
        if request.GET.get('xelon', None):
            xelon = Xelon.objects.get(numero_de_dossier=request.GET.get('xelon', None))
            data = {"prod": xelon.modele_produit}
    except Xelon.DoesNotExist:
        pass
    return JsonResponse(data)
