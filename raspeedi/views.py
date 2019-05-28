from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Raspeedi


def raspeedi_table(request):
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
    return render(request, 'raspeedi/raspeedi_table.html', context)


@login_required
def edit(request):
    """
    View for editing product data in the Raspeedi table
    :param request:
        Parameters of the request
    :return:
    """
    pass
