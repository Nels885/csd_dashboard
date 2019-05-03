from django.shortcuts import render

# Create your views here.


def table(request):
    context = {
        'title': 'Raspeedi: Table produits',
    }
    return render(request, 'raspeedi/products_table.html', context)
