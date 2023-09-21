from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from utils.django.datatables import QueryTableByArgs

from .serializers import CorvetSerializer, CORVET_COLUMN_LIST, DefaultCodeSerializer
from .models import Corvet, DefaultCode, CanRemote
from .tasks import import_corvet_task

from api.utils import TokenAuthSupportQueryString


class CorvetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Corvet.objects.all()
    serializer_class = CorvetSerializer

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            corvet = QueryTableByArgs(self.queryset, CORVET_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(corvet["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": corvet["draw"],
                "recordsTotal": corvet["total"],
                "recordsFiltered": corvet["count"]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query:
            self.queryset = Corvet.search(query)


def import_corvet_async(request):
    vin = request.GET.get('vin')
    if vin:
        task = import_corvet_task.delay(vin=vin)
        return JsonResponse({"task_id": task.id})
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


class DefaultCodeViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = DefaultCode.objects.all()
    serializer_class = DefaultCodeSerializer
    http_method_names = ['get']

    def get_queryset(self):
        product = self.request.query_params.get('prod', None)
        queryset = self.queryset
        if product:
            queryset = DefaultCode.objects.filter(ecu_type=product)
        return queryset


def canremote_async(request):
    product = request.GET.get('prod')
    if product:
        remotes = CanRemote.objects.exclude(vehicle='').filter(product=product).order_by('vehicle')
        vehicles = list(remotes.values_list('vehicle').distinct())
        return JsonResponse({"vehicles": vehicles})
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)
