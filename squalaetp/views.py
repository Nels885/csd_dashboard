from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Xelon, Corvet
from .forms import CorvetForm
from dashboard.forms import ParaErrorList


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
def xelon_edit(request, file_id):
    file = get_object_or_404(Xelon, pk=file_id)
    context = {
        'title': 'Xelon',
        'card_title': _('Modification data Xelon file: {file}'.format(file=file.numero_de_dossier)),
        'file': file,
    }

    if request.method == 'POST':
        form = CorvetForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            data = form.xml_parser('xml_data')
            if data:
                try:
                    m = Corvet(**data)
                    m.save()
                    context = {'title': "Modification réalisée avec succès !"}
                    return render(request, 'dashboard/done.html', context)
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        context['errors'] = form.errors.items()
    else:
        form = CorvetForm()
        form.fields['vin'].initial = file.vin
    context['form'] = form
    return render(request, 'squalaetp/xelon_edit.html', context)


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
                    context = {'title': "Modification réalisée avec succès !"}
                    return render(request, 'dashboard/done.html', context)
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        context['errors'] = form.errors.items()
    else:
        form = CorvetForm()
    context['form'] = form
    return render(request, 'squalaetp/corvet_insert.html', context)
