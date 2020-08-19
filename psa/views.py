from django.shortcuts import render, redirect
from django.contrib import messages

from squalaetp.models import Corvet

from utils.django.forms import ParaErrorList
from .forms import NacLicenseForm, NacUpdateForm

context = {
    'title': 'PSA'
}


def nac_tools(request):
    card_title = "Outils pour les produits NAC"
    form_license = NacLicenseForm(request.POST or None, error_class=ParaErrorList)
    form_update = NacUpdateForm(request.POST or None, error_class=ParaErrorList)
    context.update(locals())
    return render(request, 'psa/nac_tools.html', context)


def nac_license(request):
    form = NacLicenseForm(request.POST or None)
    if request.POST and form.is_valid():
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=license"
        soft = form.cleaned_data['software']
        vin = form.cleaned_data['vin']
        uin = Corvet.objects.get(vin=vin).electronique_44x
        return redirect(url.format(uin=uin, update=soft))
    for key, error in form.errors.items():
        messages.warning(request, error)
    return redirect('psa:nac_tools')


def nac_update(request):
    form = NacUpdateForm(request.POST or None)
    if request.POST and form.is_valid():
        url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={uin}&updateId={update}&type=fw"
        soft = form.cleaned_data['software']
        uin = "00000000000000000000"
        return redirect(url.format(uin=uin, update=soft))
    for key, error in form.errors.items():
        messages.warning(request, error)
    return redirect('psa:nac_tools')
