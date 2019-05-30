from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Xelon, Corvet
from .forms import CorvetForm, ParaErrorList


def xelon_table(request):
    """
    View of Xelon table page
    :param request:
        Parameters of the request
    :return:
        Xelon table page
    """
    files = Xelon.objects.all().order_by('numero_de_dossier')
    context = {
        'title': 'Xelon',
        'table_title': 'Dossiers Clients',
        'files': files
    }
    return render(request, 'squalaetp/xelon_table.html', context)


@login_required
def corvet_table(request):
    """
    View of Corvet table page, visible only if authenticated
    :param request:
        Parameters of the request
    :return:
        Corvet table page
    """
    corvets = Corvet.objects.all().order_by('vin')
    context = {
        'title': 'Corvet',
        'table_title': _('CORVET table'),
        'corvets': corvets
    }
    return render(request, 'squalaetp/corvet_table.html', context)


@login_required
def corvet_insert(request):
    """
    View of Corvet insert page, visible only if authenticated
    :param request:
        Parameters of the request
    :return:
        Corvet insert page
    """
    context = {
        'title': 'Corvet',
        'card_title': _('CORVET integration'),
    }

    if request.method == 'POST':
        form = CorvetForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            data = form.xml_parser('xml_data')
            if data:
                try:
                    m = Corvet(**data)
                    m.save()
                    return redirect('index')
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        context['errors'] = form.errors.items()
    else:
        form = CorvetForm()
    context['form'] = form
    return render(request, 'squalaetp/corvet_insert.html', context)


@login_required
def edit(request):
    pass
