from django.http import JsonResponse

from .serializers import (
    XelonSerializer, XELON_COLUMN_LIST, XelonTemporarySerializer, XELON_TEMP_COLUMN_LIST,
    SivinSerializer, SIVIN_COLUMN_LIST, SparePartSerializer, SPAREPART_COLUMN_LIST
)
from .models import Xelon, XelonTemporary, SparePart, Sivin

from utils.django.datatables import ServerSideViewSet
from utils.regex import VIN_STELLANTIS_REGEX


class XelonViewSet(ServerSideViewSet):
    queryset = Xelon.objects.filter(date_retour__isnull=False)
    serializer_class = XelonSerializer
    column_list = XELON_COLUMN_LIST
    column_start = 1

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query and query == 'pending':
            self.queryset = self.queryset.exclude(type_de_cloture__in=['Réparé', 'N/A', 'Rebut'])
        elif query and query == "vin-error":
            self.queryset = self.queryset.filter(vin_error=True).order_by('-date_retour')
        elif query and query == "corvet-error":
            self.queryset = self.queryset.filter(
                vin__regex=VIN_STELLANTIS_REGEX, vin_error=False, corvet__isnull=True).order_by('-date_retour')
        elif query:
            self.queryset = Xelon.search(query)


class TemporaryViewSet(ServerSideViewSet):
    queryset = XelonTemporary.objects.all()
    serializer_class = XelonTemporarySerializer
    column_list = XELON_TEMP_COLUMN_LIST
    column_start = 1


class StockViewSet(ServerSideViewSet):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    column_list = SPAREPART_COLUMN_LIST


class SivinViewSet(ServerSideViewSet):
    queryset = Sivin.objects.all()
    serializer_class = SivinSerializer
    column_list = SIVIN_COLUMN_LIST
    column_start = 1


def xelon_prod_async(request):
    data = {"prod": ""}
    try:
        if request.GET.get('xelon', None):
            xelon = Xelon.objects.get(numero_de_dossier=request.GET.get('xelon', None))
            data = {"prod": xelon.modele_produit}
    except Xelon.DoesNotExist:
        pass
    return JsonResponse(data)
