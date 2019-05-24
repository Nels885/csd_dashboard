from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Xelon, Corvet


def xelon_table(request):
    files = Xelon.objects.all().order_by('numero_de_dossier')
    context = {
        'title': 'Xelon',
        'table_title': 'Dossiers Clients',
        'files': files
    }
    return render(request, 'squalaetp/xelon_table.html', context)


@login_required
def corvet_table(request):
    corvets = Corvet.objects.all().order_by('vin')
    context = {
        'title': 'Xelon',
        'table_title': 'Tableau Corvet',
        'corvets': corvets
    }
    return render(request, 'squalaetp/corvet_table.html', context)


@login_required
def edit(request):
    pass
