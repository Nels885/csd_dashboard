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

    writer = csv.writer(response, delimiter=';')
    writer.writerow(
        ['vin', 'date_debut_garantie', 'date_entree_montage', 'ligne_de_produit', 'marque_commerciale', 'silhouette',
         'genre_de_produit', 'ddo', 'dgm', 'dhb', 'dhg', 'djq', 'djy', 'dkx', 'dlx', 'doi', 'dqm', 'dqs', 'drc', 'drt',
         'dti', 'dun', 'dwl', 'dwt', 'dxj', 'dyb', 'dym', 'dyr', 'dzv', 'gg8', '14f', '14j', '14k', '14l', '14r', '14x',
         '19z', '44f', '44l', '44x', '54f', '54k', '54l', '84f', '84l', '84x', '94f', '94l', '94x', 'dat', 'dcx', '19h',
         '49h', '64f', '64x', '69h', '89h', '99h', '14a', '34a', '44a', '54a', '64a', '84a', '94a', 'p4a', 'moteur',
         'transmission', '10', '14b', '20', '44b', '54b', '64b', '84b', '94b', '16p', '46p', '56p', '66p'])

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

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Xelon', 'V.I.N.', '14a', '34a', '44a', '54a', '64a', '84a', '94a', 'p4a'])

    ecus = Xelon.objects.filter(corvet__electronique_14a__isnull=False).values_list(
        'numero_de_dossier', 'vin', 'corvet__electronique_14a', 'corvet__electronique_34a', 'corvet__electronique_44a',
        'corvet__electronique_54a', 'corvet__electronique_64a', 'corvet__electronique_84a', 'corvet__electronique_94a',
        'corvet__electronique_p4a'
    )

    for ecu in ecus:
        writer.writerow(ecu)

    return response


class CorvetCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'squalaetp/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context = super().get_context_data(**kwargs)
        file = LogFile(os.path.join(CSD_ROOT, 'LOGS'), context['file'])
        with open(file.files[0], 'r') as f:
            text = f.read().replace('\n', '<br>')
        context['text'] = text
        return context
