from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Raspeedi
from .forms import RaspeediForm


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
        form = RaspeediForm(request.POST)
        if form.is_valid():
            return redirect('index')
        else:
            context['errors'] = form.errors.items()
    else:
        form = RaspeediForm()
    context['form'] = form
    return render(request, 'raspeedi/insert.html', context)
