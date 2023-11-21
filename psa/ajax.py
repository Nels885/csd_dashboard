from django.http import JsonResponse, QueryDict
from django.template.loader import render_to_string
from django.db.models import Q
from rest_framework import viewsets, permissions

from utils.django.datatables import ServerSideViewSet

from .serializers import CorvetSerializer, CORVET_COLUMN_LIST, DefaultCodeSerializer
from .models import Corvet, DefaultCode, CanRemote
from .forms import SelectCanRemoteForm
from .tasks import import_corvet_task

from api.utils import TokenAuthSupportQueryString


class CorvetViewSet(ServerSideViewSet):
    queryset = Corvet.objects.all()
    serializer_class = CorvetSerializer
    column_list = CORVET_COLUMN_LIST
    column_start = 1

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
    url = 'psa/format/fmux_rt6_remote.html'
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
            if product == "NAC":
                url = 'psa/format/fmux_nac_remote.html'
        queryset = CanRemote.objects.filter(
            Q(product=product) | Q(product='')).filter(vehicles__name__icontains=vehicle).distinct()
        nav_list = queryset.filter(type="FMUX", label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        fmux_list = queryset.filter(type="FMUX").exclude(
            label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        dsgn_list = queryset.filter(type="DSGN")
        vmf_list = CanRemote.objects.filter(type='VMF')
        return JsonResponse({
            "msg": f'Télécommande {product} pour {vehicle} sélectionnée avec succès !',
            "htmlFmux": render_to_string(url, locals(), request),
            "htmlVmf": render_to_string('psa/format/vmf_remote.html', locals(), request),
            "htmlDsgn": render_to_string('psa/format/dsgn_remote.html', locals(), request),
            "prodSelect": f"Produit {product} {vehicle}"
        })
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)
