from django.shortcuts import render

from .models import Xelon


def table(request):
    files = Xelon.objects.all().order_by('numero_de_dossier')
    context = {
        'title': 'Xelon',
        'files': files
    }
    return render(request, 'squalaetp/xelon_table.html', context)
