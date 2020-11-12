from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from utils.django.forms import ParaErrorList
from .forms import NacLicenseForm, NacUpdateForm
from .models import Corvet, Product
from dashboard.models import WebLink
from raspeedi.models import Programing

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
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=license"
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
    if corvet.electronique_14x:
        btel = Product.objects.filter(reference=corvet.electronique_14x).first()
        prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
    card_title = _('Detail Corvet data for the VIN: ') + corvet.vin
    dict_corvet = vars(corvet)
    for key in ["_state"]:
        del dict_corvet[key]
    select = "prods"
    return render(request, 'psa/detail/detail.html', locals())


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
    products = Product.objects.all().order_by('reference')
    context.update(locals())
    return render(request, 'psa/product_table.html', context)
