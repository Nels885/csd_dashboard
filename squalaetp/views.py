import csv
import datetime

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Xelon, Corvet
from .forms import CorvetForm
from dashboard.forms import ParaErrorList
from utils.decorators import group_required
from utils.xml_export_file import xml_export_file
# from utils.scraping import ScrapingCorvet


def xelon_table(request):
    """
    View of Xelon table page
    """
    files = Xelon.objects.filter(date_retour__isnull=False).order_by('numero_de_dossier')
    context = {
        'title': 'Xelon',
        'table_title': 'Dossiers Clients',
        'files': files
    }
    return render(request, 'squalaetp/xelon_table.html', context)


def xelon_detail(request, file_id):
    """
    detailed view of Xelon data for a file
    :param file_id:
        Xelon file id
    """
    file = get_object_or_404(Xelon, pk=file_id)
    context = {
        'title': 'Xelon',
        'card_title': _('Detail data for the Xelon file: ') + file.numero_de_dossier,
        'file': file,
    }
    return render(request, 'squalaetp/xelon_detail.html', context)


def ihm(request):
    return redirect('squalaetp:ihm-detail', file_id=1)


def ihm_detail(request, file_id):
    file = get_object_or_404(Xelon, pk=file_id)
    if file.corvet.exists():
        corvet = get_object_or_404(Corvet, vin=file.vin)
    else:
        corvet = None
    form = CorvetForm()
    form.fields['vin'].initial = file.vin
    context = {
        'title': 'IHM Extraction',
        'card_title': _('Detail data for the Xelon file: ') + file.numero_de_dossier,
        'file': file,
        'corvet': corvet,
        'form': form,
        'redirect': request.META.get('HTTP_REFERER')
    }
    return render(request, 'squalaetp/ihm_detail.html', context)


@login_required
@group_required('cellule', 'technician')
def xelon_edit(request, file_id):
    """
    View for changing Xelon data
    :param file_id:
        Xelon file id to edit
    """
    file = get_object_or_404(Xelon, pk=file_id)
    context = {
        'title': 'Xelon',
        'card_title': _('Modification data Xelon file: ') + file.numero_de_dossier,
        'file': file,
    }

    if request.method == 'POST':
        form = CorvetForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            data = form.xml_parser('xml_data')
            if data:
                try:
                    xml_export_file(form.cleaned_data['xml_data'], form.cleaned_data['vin'])
                    m = Corvet(**data)
                    m.save()
                    m.xelons.add(file)
                    context = {'title': _('Modification done successfully!')}
                    return render(request, 'dashboard/done.html', context)
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        context['errors'] = form.errors.items()
    else:
        # corvet = ScrapingCorvet()
        form = CorvetForm()
        form.fields['vin'].initial = file.vin
        # form.fields['xml_data'].initial = corvet.result(file.vin)
        # corvet.close()
    context['form'] = form
    return render(request, 'squalaetp/xelon_edit.html', context)


@login_required
def corvet_table(request):
    """
    View of Corvet table page, visible only if authenticated
    """
    corvets = Corvet.objects.all().order_by('vin')
    context = {
        'title': 'Corvet',
        'table_title': _('CORVET table'),
        'corvets': corvets
    }
    return render(request, 'squalaetp/corvet_table.html', context)


@login_required
def corvet_detail(request, vin):
    """
    detailed view of Corvet data for a file
    :param vin:
        VIN for Corvet data
    """
    corvet = get_object_or_404(Corvet, vin=vin)
    dict_corvet = vars(corvet)
    for key in ["_state"]:
        del dict_corvet[key]
    context = {
        'title': 'Corvet',
        'card_title': _('Detail Corvet data for the VIN: ') + corvet.vin,
        'dict_corvet': dict_corvet,
        'redirect': request.META.get('HTTP_REFERER')
    }
    return render(request, 'squalaetp/corvet_detail.html', context)


@login_required
@group_required('cellule', 'technician')
def corvet_insert(request):
    """
    View of Corvet insert page, visible only if authenticated
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
                    context = {'title': _('Modification done successfully!')}
                    return render(request, 'dashboard/done.html', context)
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        context['errors'] = form.errors.items()
    else:
        form = CorvetForm()
    context['form'] = form
    return render(request, 'squalaetp/corvet_insert.html', context)


@login_required
@group_required('cellule', 'technician')
def export_corvet_csv(request):
    date = datetime.datetime.now()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="corvet_{}.csv"'.format(date.strftime("%y-%m-%d_%H-%M"))

    writer = csv.writer(response)
    writer.writerow(
        ['vin', 'date_debut_garantie', 'date_entree_montage', 'ligne_de_produit', 'marque_commerciale', 'silhouette',
         'genre_de_produit', 'ddo', 'dgm', 'dhb', 'dhg', 'djq', 'djy', 'dkx', 'dlx', 'doi', 'dqm', 'dqs', 'drc', 'drt',
         'dti', 'dun', 'dwl', 'dwt', 'dxj', 'dyb', 'dym', 'dyr', 'dzv', 'gg8', '14f', '14j', '14k', '14l', '14r', '14x',
         '19z', '44f', '44l', '44x', '54f', '54k', '54l', '84f', '84l', '84x', '94f', '94l', '94x', 'dat', 'dcx', '19h',
         '49h', '64f', '64x', '69h', '89h', '99h', '14a', '34a', '44a', '54a', '64a', '84a', '94a', 'p4a', 'moteur',
         'transmission', '10', '14b', '20', '44b', '54b', '64b', '84b', '94b'])

    corvets = Corvet.objects.all().values_list()
    for corvet in corvets:
        print(corvet)
        writer.writerow(corvet)

    return response
