from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Raspeedi


def table(request):
    products = Raspeedi.objects.all().order_by('ref_boitier')
    context = {
        'title': 'Raspeedi',
        'products': products
    }
    return render(request, 'raspeedi/products_table.html', context)


@login_required
def edit(request):
    pass
