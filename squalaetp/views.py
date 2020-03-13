import csv
import datetime

from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField
from bootstrap_modal_forms.generic import BSModalCreateView

from .models import Xelon, Corvet
from .forms import CorvetForm, CorvetModalForm
from dashboard.forms import ParaErrorList
from utils.django.decorators import group_required
from utils.file.export import xml_corvet_file
from utils.file import LogFile, os
from utils.conf import CSD_ROOT

# from utils.scraping import ScrapingCorvet


@login_required
def xelon_table(request):
    """
    View of Xelon table page
    """
    form = CorvetForm()
    context = {
        'title': 'Xelon',
        'table_title': 'Dossiers Clients',
        # 'files': files
        'form': form
    }
    return render(request, 'squalaetp/xelon_table.html', context)


@login_required
def detail(request, file_id):
    file = get_object_or_404(Xelon, pk=file_id)
    if file.corvet.exists():
        corvet = get_object_or_404(Corvet, vin=file.vin)
        raspeedi = corvet.raspeedi.first()
        dict_corvet = vars(corvet)
        for key in ["_state"]:
            del dict_corvet[key]
        dict_corvet = vars(corvet)
    else:
        corvet = dict_corvet = raspeedi = None
    form = CorvetForm()
    form.fields['vin'].initial = file.vin
    context = {
        'title': file.numero_de_dossier,
        'file': file,
        'corvet': corvet,
        'raspeedi': raspeedi,
        'dict_corvet': dict_corvet,
        'form': form,
        'select': 'xelon',
        'redirect': request.META.get('HTTP_REFERER'),
        # 'log_file': LogFile(CSD_ROOT, file.numero_de_dossier)
        'log_file': None
    }
    return render(request, 'squalaetp/detail.html', context)


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
                    xml_corvet_file(form.cleaned_data['xml_data'], form.cleaned_data['vin'])
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
@group_required('cellule', 'technician')
def ajax_xelon(request):
    """
    View for changing Xelon data
    """
    if request.method == 'POST':
        form = CorvetForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            file_id = request.POST.get('file_id')
            file = get_object_or_404(Xelon, pk=file_id)
            data = form.xml_parser('xml_data')
            if data:
                try:
                    xml_corvet_file(form.cleaned_data['xml_data'], form.cleaned_data['vin'])
                    m = Corvet(**data)
                    m.save()
                    m.xelons.add(file)
                    context = {'message': _('Modification done successfully!')}
                    messages.success(request, context['message'])
                    return JsonResponse(context, status=200)
                except TypeError:
                    form.add_error('internal', _('An internal error has occurred. Thank you recommend your request'))
        print(form.errors)
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


@login_required
def corvet_table(request):
    """
    View of Corvet table page, visible only if authenticated
    """
    # corvets_list = Corvet.objects.all().order_by('vin')

    context = {
        'title': 'Corvet',
        'table_title': _('CORVET table'),
        # 'corvets': corvets
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

    writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
    writer.writerow(
        ['V.I.N.', 'DATE_DEBUT_GARANTIE', 'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE', 'SILHOUETTE',
         'GENRE_DE_PRODUIT', 'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM', 'DQS', 'DRC', 'DRT',
         'DTI', 'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J', '14K', '14L', '14R', '14X',
         '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F', '94L', '94X', 'DAT', 'DCX', '19H',
         '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A', '64A', '84A', '94A', 'P4A', 'MOTEUR',
         'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B', '16P', '46P', '56P', '66P'])

    corvets = Corvet.objects.all().values_list()
    for corvet in corvets:
        writer.writerow(corvet)

    return response


@login_required()
@group_required('cellule', 'technician')
def export_ecu_csv(request):
    date = datetime.datetime.now()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ecu_{}.csv"'.format(date.strftime("%y-%m-%d_%H-%M"))

    writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
    writer.writerow(['Numero de dossier', 'V.I.N.', 'DATE_DEBUT_GARANTIE', '14A', '34A', '44A', '54A', '64A', '84A',
                     '94A', 'P4A'])

    ecus = Xelon.objects.filter(corvet__electronique_14a__isnull=False).annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    ecus = ecus.values_list(
        'numero_de_dossier', 'vin', 'date_debut_garantie', 'corvet__electronique_14a',
        'corvet__electronique_34a', 'corvet__electronique_44a', 'corvet__electronique_54a', 'corvet__electronique_64a',
        'corvet__electronique_84a', 'corvet__electronique_94a', 'corvet__electronique_p4a'
    )

    for ecu in ecus:
        writer.writerow(ecu)

    return response


class CorvetCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'squalaetp/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super(CorvetCreateView, self).get_context_data(**kwargs)
        context['modal_title'] = _('CORVET integration')
        return context

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class LogFileView(LoginRequiredMixin, TemplateView):
    template_name = 'squalaetp/modal/log_file.html'

    def get_context_data(self, **kwargs):
        context = super(LogFileView, self).get_context_data(**kwargs)
        file = LogFile(os.path.join(CSD_ROOT, 'LOGS'), context['file'])
        with open(file.files[0], 'r') as f:
            text = f.read().replace('\n', '<br>')
        context['text'] = text
        return context
