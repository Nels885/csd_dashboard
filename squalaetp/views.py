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
    title = 'Xelon'
    form = CorvetForm()
    if request.GET.get('filter') and request.GET.get('filter') == "pending":
        table_title = 'Dossiers en cours'
        files = Xelon.objects.exclude(type_de_cloture__exact='Réparé').filter(
            date_retour__isnull=False).order_by('-date_retour')
        return render(request, 'squalaetp/xelon_table.html', locals())
    else:
        table_title = 'Dossiers Clients'
        return render(request, 'squalaetp/all_xelon_table.html', locals())


@login_required
def detail(request, file_id):
    xelon = get_object_or_404(Xelon, pk=file_id)
    title = xelon.numero_de_dossier
    if xelon.corvet.exists():
        corvet = get_object_or_404(Corvet, vin=xelon.vin)
        raspeedi = corvet.raspeedi.first()
        dict_corvet = vars(corvet)
        for key in ["_state"]:
            del dict_corvet[key]
        dict_corvet = vars(corvet)
    else:
        corvet = dict_corvet = raspeedi = None
    form = CorvetForm()
    form.fields['vin'].initial = xelon.vin
    select = 'xelon'
    redirect = request.META.get('HTTP_REFERER')
    # 'log_file': LogFile(CSD_ROOT, file.numero_de_dossier)
    return render(request, 'squalaetp/detail.html', locals())


@permission_required('squalaetp.view_xelon')
def xelon_edit(request, file_id):
    """
    View for changing Xelon data
    :param file_id:
        Xelon file id to edit
    """
    title = 'Xelon'
    file = get_object_or_404(Xelon, pk=file_id)
    corvet = Corvet.objects.filter(vin=file.vin).first()
    card_title = _('Modification data Xelon file: ') + file.numero_de_dossier
    form = CorvetForm(request.POST or None, instance=corvet, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        form.save()
        form.save_m2m()
        context = {'title': _('Modification done successfully!')}
        return render(request, 'dashboard/done.html', context)
    errors = form.errors.items()
    # corvet = ScrapingCorvet()
    # form.fields['xml_data'].initial = corvet.result(file.vin)
    # corvet.close()
    return render(request, 'squalaetp/xelon_edit.html', locals())


@permission_required('squalaetp.view_xelon')
def ajax_xelon(request):
    """
    View for changing Xelon data
    """
    file_id = request.POST.get('file_id')
    file = get_object_or_404(Xelon, pk=file_id)
    corvet = Corvet.objects.filter(vin=file.vin).first()
    form = CorvetForm(request.POST or None, instance=corvet, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        xml_corvet_file(form.cleaned_data['xml_data'], form.cleaned_data['vin'])
        form.save()
        context = {'message': _('Modification done successfully!')}
        messages.success(request, context['message'])
        return JsonResponse(context, status=200)
    print(form.errors)
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


@permission_required('squalaetp.view_corvet')
def corvet_table(request):
    """
    View of Corvet table page, visible only if authenticated
    """
    # corvets_list = Corvet.objects.all().order_by('vin')
    title = 'Corvet'
    table_title = _('CORVET table')
    form = ExportCorvetForm()
    return render(request, 'squalaetp/corvet_table.html', locals())


@permission_required('squalaetp.view_corvet')
def corvet_detail(request, vin):
    """
    detailed view of Corvet data for a file
    :param vin:
        VIN for Corvet data
    """
    title = 'Corvet'
    corvet = get_object_or_404(Corvet, vin=vin)
    card_title = _('Detail Corvet data for the VIN: ') + corvet.vin
    dict_corvet = vars(corvet)
    for key in ["_state"]:
        del dict_corvet[key]
    # redirect = request.META.get('HTTP_REFERER')
    return render(request, 'squalaetp/corvet_detail.html', locals())


@permission_required('squalaetp.add_corvet')
def corvet_insert(request):
    """
    View of Corvet insert page, visible only if authenticated
    """
    title = 'Corvet'
    card_title = _('CORVET integration')
    form = CorvetForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        form.save()
        context = {'title': _('Modification done successfully!')}
        return render(request, 'dashboard/done.html', context)
    errors = form.errors.items()
    return render(request, 'squalaetp/corvet_insert.html', locals())


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
        context['modal_title'] = _('CORVET update for %(file)s' % {'file': file})
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
