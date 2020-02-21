from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib import messages

from .models import Raspeedi, UnlockProduct, UserProfile
from .forms import RaspeediForm, UnlockForm
from dashboard.forms import ParaErrorList
from squalaetp.models import Xelon
from utils.django.decorators import group_required


@login_required
def table(request):
    """
    View of the Raspeedi table page
    :param request:
        Parameters of the request
    :return:
        Raspeedi table page
    """
    products = Raspeedi.objects.all().order_by('ref_boitier')
    context = {
        'title': 'Raspeedi',
        'table_title': _('Table Products Telematics PSA'),
        'products': products
    }
    return render(request, 'raspeedi/table.html', context)


def detail(request, ref_case):
    """
    detailed view of Raspeedi data for a product
    :param ref_case:
        Ref case of product
    """
    product = get_object_or_404(Raspeedi, ref_boitier=ref_case)
    dict_prod = vars(product)
    for key in ["_state"]:
        del dict_prod[key]
    context = {
        'title': 'Raspeedi',
        'card_title': _('Detail raspeedi data for the ref case of Product: ') + str(product.ref_boitier),
        'dict_prod': dict_prod,
    }
    return render(request, 'raspeedi/detail.html', context)


@login_required
def unlock_prods(request):
    unlock = UnlockProduct.objects.all().order_by('created_at')
    context = {
        'title': 'Raspeedi',
        'table_title': _('Unlocking product for programming'),
        'products': unlock
    }
    if request.method == 'POST':
        user = UserProfile.objects.get(user_id=request.user.id)
        form = UnlockForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            if request.user.has_perm('raspeedi.add_unlockproduct'):
                unlock = form.cleaned_data['unlock']
                product = get_object_or_404(Xelon, numero_de_dossier=unlock)
                UnlockProduct.objects.create(user=user, unlock=product)
                messages.success(request, _('Adding the Xelon number %(xelon)s successfully') % {'xelon': unlock})
            else:
                messages.warning(request, _('You do not have the required permissions'))
        context['errors'] = form.errors.items()
    else:
        form = UnlockForm()
    context['form'] = form
    return render(request, 'raspeedi/unlock_prods.html', context)


@login_required
@group_required('cellule', 'technician')
def insert(request):
    context = {
        'title': 'Raspeedi',
        'card_title': _('RASPEEDI integration'),
    }
    if request.method == 'POST':
        form = RaspeediForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            ref_case = form.cleaned_data['ref_boitier']
            ref = Raspeedi.objects.filter(ref_boitier=ref_case)
            if not ref.exists():
                Raspeedi.objects.create(**form.cleaned_data)
                messages.success(request, _('Added successfully!'))
        context['errors'] = form.errors.items()
    else:
        form = RaspeediForm()
    context['form'] = form
    return render(request, 'raspeedi/insert.html', context)


@login_required
@group_required('cellule', 'technician')
def edit(request, ref_case):
    product = get_object_or_404(Raspeedi, ref_boitier=ref_case)
    form = RaspeediForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
    context = {
        'title': 'Raspeedi',
        'card_title': _('Modification data RASPEEDI for ref case: ') + str(product.ref_boitier),
        'url': 'raspeedi:edit',
        'prod': product,
        'form': form,
    }
    return render(request, 'raspeedi/edit.html', context)
