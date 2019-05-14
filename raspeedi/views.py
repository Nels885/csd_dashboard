from django.shortcuts import render

from .models import Raspeedi


def table(request):
    products = Raspeedi.objects.all().order_by('ref_boitier')
    context = {
        'title': 'Raspeedi',
        'products': products
    }
    return render(request, 'raspeedi/products_table.html', context)
