# import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.forms.models import model_to_dict
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from utils.django.forms import ParaErrorList
from utils.django.datatables import QueryTableByArgs
from utils.django.urls import reverse_lazy, http_referer
from .serializers import CorvetSerializer, CORVET_COLUMN_LIST
from .forms import NacLicenseForm, NacUpdateIdLicenseForm, NacUpdateForm, CorvetModalForm
from .models import Corvet, Multimedia
from .tasks import import_corvet_task
from dashboard.models import WebLink
from squalaetp.models import Sivin
from raspeedi.models import Programing
from reman.models import EcuType

context = {
    'title': 'Info PSA'
}


def nac_tools(request):
    form_license = NacLicenseForm(request.POST or None, error_class=ParaErrorList)
    form_id_license = NacUpdateIdLicenseForm(request.POST or None, error_class=ParaErrorList)
    form_update = NacUpdateForm(request.POST or None, error_class=ParaErrorList)
    web_links = WebLink.objects.filter(type="PSA")
    context.update(locals())
    return render(request, 'psa/nac_tools.html', context)


def nac_license(request):
    form = NacLicenseForm(request.POST or None)
    if request.POST and form.is_valid():
        # url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload"
        # payload = {
        #     "mediaVersion": form.cleaned_data['software'].update_id,
        #     "uin": form.cleaned_data['uin']
        # }
        # response = requests.get(url, params=payload, allow_redirects=True)
        # print(response.url)
        # if response.status_code == 200:
        #     return redirect(response.url)
        # messages.warning(request, 'Fichier non trouvé !')
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload?mediaVersion={update}&uin={uin}"
        soft = form.cleaned_data['software']
        uin = form.cleaned_data['uin']
        return redirect(url.format(uin=uin, update=soft.update_id))
    for key, error in form.errors.items():
        messages.warning(request, error)
    return redirect('psa:nac_tools')


def nac_update_id_license(request):
    form = NacUpdateIdLicenseForm(request.POST or None)
    if request.POST and form.is_valid():
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload?mediaVersion={update}&uin={uin}"
        update_id = form.cleaned_data['update_id']
        uin = form.cleaned_data['uin']
        return redirect(url.format(uin=uin, update=update_id))
    for key, error in form.errors.items():
        messages.warning(request, error)
    return redirect('psa:nac_tools')


def nac_update(request):
    form = NacUpdateForm(request.POST or None)
    if request.POST and form.is_valid():
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=fw"
        soft = form.cleaned_data['software']
        uin = "00000000000000000000"
        return redirect(url.format(uin=uin, update=soft.update_id))
    for key, error in form.errors.items():
        messages.warning(request, error)
    return redirect('psa:nac_tools')


def majestic_web(request):
    type = request.GET.get('type')
    update_id = request.GET.get('updateId')
    uin = request.GET.get('uin')
    if type == 'license':
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/LicenseDownload?mediaVersion={update}&uin={uin}"
        return redirect(url.format(uin=uin, update=update_id))
    elif type == 'fw':
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=fw"
        uin = "00000000000000000000"
        return redirect(url.format(uin=uin, update=update_id))
    return redirect(http_referer(request))


def useful_links(request):
    web_links = WebLink.objects.filter(type="PSA")
    context.update(locals())
    return render(request, 'psa/useful_links.html', context)


class CorvetView(PermissionRequiredMixin, TemplateView):
    template_name = 'psa/corvet_table.html'
    permission_required = 'psa.view_corvet'

    def get_context_data(self, **kwargs):
        context = super(CorvetView, self).get_context_data(**kwargs)
        context['title'] = 'Info PSA'
        context['table_title'] = _('CORVET table')
        context['query_param'] = self.request.GET.get('filter', '')
        return context


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


@permission_required('psa.view_corvet')
def corvet_detail(request, vin):
    """
    detailed view of Corvet data for a file
    :param vin:
        VIN for Corvet data
    """
    collapse = {
        "media": True, "prog": True, "emf": True, "cmm": True, "display": True, "audio": True, "ecu": True, "bsi": True,
        "cmb": True
    }
    corvet = get_object_or_404(Corvet, vin=vin)
    if corvet.electronique_14x.isdigit():
        prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
    if corvet.electronique_14a.isdigit():
        cmm = EcuType.objects.filter(hw_reference=corvet.electronique_14a).first()
    card_title = _('Detail Corvet data for the VIN: ') + corvet.vin
    dict_corvet = model_to_dict(corvet)
    if Sivin.objects.filter(codif_vin=vin):
        dict_sivin = model_to_dict(Sivin.objects.filter(codif_vin=vin).first())
    select = "prods"
    context.update(locals())
    return render(request, 'psa/detail/detail.html', context)


class CorvetCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'psa.add_corvet'
    template_name = 'psa/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super(CorvetCreateView, self).get_context_data(**kwargs)
        context['modal_title'] = _('CORVET integration')
        return context

    def get_success_url(self):
        if not self.request.is_ajax():
            return reverse_lazy('psa:corvet_detail', args=[self.object.pk])
        return http_referer(self.request)


class CorvetUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for updating Corvet and VIN data """
    model = Corvet
    permission_required = 'psa.add_corvet'
    template_name = 'psa/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('CORVET update for %(vin)s' % {'vin': self.object.vin})
        return context

    def get_success_url(self):
        return reverse_lazy('psa:corvet_detail', args=[self.object.pk])


@permission_required('psa.view_multimedia')
def product_table(request):
    """
    View of the product table page
    :param request:
        Parameters of the request
    :return:
        Product table page
    """
    table_title = _('Products PSA table')
    products = Multimedia.objects.all()
    context.update(locals())
    return render(request, 'psa/product_table.html', context)


def import_corvet_async(request):
    vin = request.GET.get('vin')
    if vin:
        task = import_corvet_task.delay(vin=vin)
        return JsonResponse({"task_id": task.id})
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)
