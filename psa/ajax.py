from django.http import JsonResponse, QueryDict
from django.template.loader import render_to_string
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from utils.django.datatables import QueryTableByArgs

from .serializers import CorvetSerializer, CORVET_COLUMN_LIST, DefaultCodeSerializer
from .models import Corvet, DefaultCode, CanRemote
from .forms import SelectCanRemoteForm
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
        remotes = CanRemote.objects.filter(product=product).exclude(vehicles__name='').order_by('vehicles__name')
        vehicles = list(remotes.values_list('vehicles__name').distinct())
        return JsonResponse({"vehicles": vehicles})
    if request.method == 'POST':
        vehicle = ""
        form_data = QueryDict(request.POST['form'].encode('ASCII'))
        form = SelectCanRemoteForm(form_data)
        if form.is_valid():
            name = form.cleaned_data.get('name', None)
            product = form.cleaned_data.get('product')
            vehicle = form.cleaned_data.get('vehicle')
        queryset = CanRemote.objects.filter(
            Q(product=product) | Q(product='')).filter(vehicles__name__icontains=vehicle).distinct()
        nav_list = queryset.filter(type="FMUX", label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        fmux_list = queryset.filter(type="FMUX").exclude(
            label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        dsgn_list = queryset.filter(type="DSGN")
        vmf_list = CanRemote.objects.filter(type='VMF')
        return JsonResponse({
            "msg": f'Télécommande {product} pour {vehicle} sélectionnée avec succès !',
            "htmlFmux": render_to_string('psa/format/fmux_rt6_remote.html', locals(), request),
            "htmlVmf": render_to_string('psa/format/vmf_remote.html', locals(), request),
            "htmlDsgn": render_to_string('psa/format/dsgn_remote.html', locals(), request)
        })
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)
