from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Raspeedi
from .forms import RaspeediForm
from dashboard.forms import ParaErrorList


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
        'card_title': _('Detail raspeedi data for the ref case of Product: {file}'.format(file=product.ref_boitier)),
        'dict_prod': dict_prod,
    }
    return render(request, 'raspeedi/detail.html', context)


@login_required
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
                context = {'title': _('Added successfully!')}
                return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = RaspeediForm()
    context['form'] = form
    return render(request, 'raspeedi/insert.html', context)


@login_required
def edit(request, ref_case):
    product = get_object_or_404(Raspeedi, ref_boitier=ref_case)
    form = RaspeediForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        context = {'title': _('Modification done successfully!')}
        return render(request, 'dashboard/done.html', context)
    context = {
        'title': 'Raspeedi',
        'card_title': _('Modification data RASPEEDI for ref case: {ref_case}'.format(ref_case=product.ref_boitier)),
        'url': 'raspeedi:edit',
        'prod': product,
        'form': form,
    }
    return render(request, 'raspeedi/edit.html', context)
