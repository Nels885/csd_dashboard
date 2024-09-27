import requests
import shutil

from pathlib import Path
from json import JSONDecodeError
from django.http import JsonResponse, QueryDict
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings

from utils.django.datatables import ServerSideViewSet
from constance import config

from .serializers import CorvetSerializer, CORVET_COLUMN_LIST, DTCServerSideSerializer, DTC_COLUMN_LIST
from .models import Corvet, DefaultCode, CanRemote
from .forms import SelectCanRemoteForm
from .tasks import import_corvet_task


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


class DTCServerSodeViewSet(ServerSideViewSet):
    queryset = DefaultCode.objects.all()
    serializer_class = DTCServerSideSerializer
    column_list = DTC_COLUMN_LIST
    column_start = 1


def canremote_async(request):
    product = request.GET.get('prod')
    url = 'psa/format/fmux_default_remote.html'
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
            if product == "RT6":
                url = 'psa/format/fmux_rt6_remote.html'
        queryset = CanRemote.objects.filter(
            Q(product=product)).filter(vehicles__name__icontains=vehicle).distinct()
        vol_up, vol_down = CanRemote.get_volume(product, vehicle)
        nav_list = queryset.filter(type="FMUX", label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        fmux_list = queryset.filter(type="FMUX").exclude(
            label__in=['VOL+', 'VOL-', 'UP', 'DOWN', 'SEEK-UP', 'SEEK-DWN'])
        dsgn_list = queryset.filter(type="DSGN")
        data = {
            "msg": f"Télécommande {product} pour {vehicle} sélectionnée avec succès !",
            "htmlFmux": render_to_string(url, locals(), request),
            "htmlDsgn": render_to_string("psa/format/dsgn_remote.html", locals(), request),
            "prodSelect": f"Produit {product} {vehicle}"
        }
        if product != "IVI":
            context = {"vmf_list": CanRemote.objects.filter(type='VMF')}
            data["htmlVmf"] = render_to_string('psa/format/vmf_remote.html', context, request)
        return JsonResponse(data)
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


def majestic_web_async(request):
    type_dl = request.GET.get('type')
    update_id = request.GET.get('updateId')
    uin = request.GET.get('uin')
    if type_dl == 'license':
        response = download_nac_license_file(update_id, uin)
        if response.status_code == 200:
            try:
                return JsonResponse({"data": response.json(), "msg": "License not found !!!"}, status=200)
            except JSONDecodeError:
                return JsonResponse({"url": response.url}, status=200)
    elif type_dl == 'fw':
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=fw"
        uin = "00000000000000000000"
        return JsonResponse({"url": url.format(uin=uin, update=update_id)}, status=200)
    return JsonResponse({"msg": "Majestic-web not response !!!"}, status=400)


def download_nac_license_file(update_id, uin):
    url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload"
    payload = {"mediaVersion": update_id, "uin": uin}
    session = requests.Session()
    if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
        proxy = f"{config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}"
        session.proxies = {'http': proxy, 'https': proxy}
    response = session.get(url, params=payload, allow_redirects=True, stream=True)
    if response.status_code == 200:
        filename = response.headers.get('Content-Disposition', '').split('filename=')[-1]
        if filename and (".key" in filename or ".rar" in filename):
            output_file = Path(settings.MEDIA_ROOT, "PSA/nac_license/", filename)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(output_file, "wb") as f:
                shutil.copyfileobj(response.raw, f)
    return response
