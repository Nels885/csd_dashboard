# import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.forms.models import model_to_dict
from bootstrap_modal_forms.generic import BSModalCreateView

from utils.django.forms import ParaErrorList
from .forms import NacLicenseForm, NacUpdateForm, CorvetModalForm, CorvetForm
from .models import Corvet, Multimedia
from dashboard.models import WebLink
from raspeedi.models import Programing
from reman.models import EcuType

context = {
    'title': 'Info PSA'
}


def nac_tools(request):
    form_license = NacLicenseForm(request.POST or None, error_class=ParaErrorList)
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
        return context


@permission_required('psa.view_corvet')
def corvet_detail(request, vin):
    """
    detailed view of Corvet data for a file
    :param vin:
        VIN for Corvet data
    """
    title = f'Info CORVET : {vin}'
    corvet = get_object_or_404(Corvet, vin=vin)
    if corvet.electronique_14x.isdigit():
        prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
    if corvet.electronique_14a.isdigit():
        cmm = EcuType.objects.filter(hw_reference=corvet.electronique_14a).first()
    card_title = _('Detail Corvet data for the VIN: ') + corvet.vin
    dict_corvet = model_to_dict(corvet)
    select = "prods"
    return render(request, 'psa/detail/detail.html', locals())


@permission_required('psa.add_corvet')
def corvet_insert(request):
    """
    View of Corvet insert page, visible only if authenticated
    """
    title = 'Corvet'
    card_title = _('CORVET integration')
    form = CorvetForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        form.save()
        context = {'title': _('Modification done successfully!')}
        return render(request, 'dashboard/done.html', context)
    errors = form.errors.items()
    return render(request, 'psa/corvet_insert.html', locals())


class CorvetCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'psa.add_corvet'
    template_name = 'psa/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super(CorvetCreateView, self).get_context_data(**kwargs)
        context['modal_title'] = _('CORVET integration')
        return context

    def form_valid(self, form):
        if not self.request.is_ajax():
            form.save()
        return super(CorvetCreateView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


@permission_required('psa.view_product')
def product_table(request):
    """
    View of the product table page
    :param request:
        Parameters of the request
    :return:
        Product table page
    """
    table_title = _('Products PSA table')
    products = Multimedia.objects.all().order_by('hw_reference')
    context.update(locals())
    return render(request, 'psa/product_table.html', context)
