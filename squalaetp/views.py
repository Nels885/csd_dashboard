from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView

from .models import Xelon, Corvet
from .forms import CorvetForm, CorvetModalForm
from import_export.forms import ExportCorvetForm
from dashboard.forms import ParaErrorList
from utils.file.export import xml_corvet_file
from utils.file import LogFile, os
from utils.conf import CSD_ROOT

# from utils.scraping import ScrapingCorvet


@login_required
def xelon_table(request):
    context = {
        'title': 'Xelon',
        'form': CorvetForm()
    }
    query = request.GET.get('filter')
    if query and query == "pending":
        files = Xelon.objects.exclude(type_de_cloture__exact='Réparé').filter(
            date_retour__isnull=False).order_by('-date_retour')
        context.update({
            'table_title': 'Dossiers en cours',
            'files': files
        })
        return render(request, 'squalaetp/xelon_table.html', context)
    else:
        context['table_title'] = 'Dossiers Clients'
        return render(request, 'squalaetp/all_xelon_table.html', context)


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


@permission_required('squalaetp.view_xelon')
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


@permission_required('squalaetp.view_xelon')
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


@permission_required('squalaetp.view_corvet')
def corvet_table(request):
    """
    View of Corvet table page, visible only if authenticated
    """
    # corvets_list = Corvet.objects.all().order_by('vin')
    context = {
        'title': 'Corvet',
        'table_title': _('CORVET table'),
        'form': ExportCorvetForm(),
    }
    return render(request, 'squalaetp/corvet_table.html', context)


@permission_required('squalaetp.view_corvet')
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


@permission_required('squalaetp.add_corvet')
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
            form.save()
            context = {'title': _('Modification done successfully!')}
            return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = CorvetForm()
    context['form'] = form
    return render(request, 'squalaetp/corvet_insert.html', context)


class CorvetCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = ['squalaetp.add_corvet']
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


class SqualaetpUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Xelon
    permission_required = ['squalaetp.change_xelon', 'squalaetp.change_corvet']
    template_name = 'squalaetp/modal/corvet_form.html'
    form_class = CorvetModalForm
    success_message = _('Success: Squalaetp data was updated.')

    def get_context_data(self, **kwargs):
        context = super(SqualaetpUpdateView, self).get_context_data(**kwargs)
        file = self.object.numero_de_dossier
        context['modal_title'] = _('CORVET update for {}'.format(file))
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
