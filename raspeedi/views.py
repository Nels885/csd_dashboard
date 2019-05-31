from django.shortcuts import render, redirect
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
        'table_title': 'Tableau Produits Télématique PSA',
        'products': products
    }
    return render(request, 'raspeedi/table.html', context)


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
                Raspeedi.objects.create(form)
                return redirect('index')
        context['errors'] = form.errors.items()
    else:
        form = RaspeediForm()
    context['form'] = form
    return render(request, 'raspeedi/insert.html', context)
