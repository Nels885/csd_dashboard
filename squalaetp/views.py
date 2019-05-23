from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Xelon


def xelon_table(request):
    files = Xelon.objects.all().order_by('numero_de_dossier')
    context = {
        'title': 'Xelon',
        'files': files
    }
    return render(request, 'squalaetp/xelon_table.html', context)


@login_required
def edit(request):
    pass
