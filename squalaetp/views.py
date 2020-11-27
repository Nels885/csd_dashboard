from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView
from django.forms.models import model_to_dict

from .models import Xelon, Stock
from psa.models import Corvet, Multimedia
from raspeedi.models import Programing
from .forms import IhmForm, XelonModalForm, IhmEmailModalForm
from psa.forms import CorvetForm
from dashboard.forms import ParaErrorList
from utils.file.export import xml_corvet_file
from utils.file import LogFile, os
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict


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
        return render(request, 'squalaetp/ajax_xelon_table.html', locals())


@login_required
def stock_table(request):
    """ View of SparePart table page """
    title = 'Xelon'
    table_title = 'Pièces détachées'
    stocks = Stock.objects.all()
    return render(request, 'squalaetp/stock_table.html', locals())


@login_required
def detail(request, file_id):
    xelon = get_object_or_404(Xelon, pk=file_id)
    title = f"{xelon.numero_de_dossier} - {xelon.modele_vehicule} - {xelon.vin}"
    if xelon.corvet:
        corvet = get_object_or_404(Corvet, vin=xelon.vin)
        if corvet.electronique_14x:
            btel = Multimedia.objects.filter(hw_reference=corvet.electronique_14x).first()
            prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
        elif corvet.electronique_14f:
            btel = Multimedia.objects.filter(hw_reference=corvet.electronique_14f).first()
        dict_corvet = model_to_dict(corvet)
    form = IhmForm(instance=xelon.corvet,
                   initial=model_to_dict(xelon, fields=('vin', 'modele_produit', 'modele_vehicule')))
    select = 'xelon'
    redirect = request.META.get('HTTP_REFERER')
    # 'log_file': LogFile(CSD_ROOT, file.numero_de_dossier)
    return render(request, 'squalaetp/detail/detail.html', locals())


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


class SqualaetpUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Xelon
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'psa/modal/corvet_form.html'
    form_class = XelonModalForm
    success_message = _('Success: Squalaetp data was updated.')

    def get_context_data(self, **kwargs):
        context = super(SqualaetpUpdateView, self).get_context_data(**kwargs)
        file = self.object.numero_de_dossier
        context['modal_title'] = _('CORVET update for %(file)s' % {'file': file})
        return context

    def form_valid(self, form):
        data = form.cleaned_data['xml_data']
        defaults = defaults_dict(Corvet, data, 'vin')
        obj, created = Corvet.objects.update_or_create(vin=form.cleaned_data['vin'], defaults=defaults)
        self.object.corvet = obj
        return super(SqualaetpUpdateView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class IhmEmailFormView(PermissionRequiredMixin, BSModalFormView):
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm
    success_message = _('Success: Squalaetp data was updated.')

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class LogFileView(LoginRequiredMixin, TemplateView):
    template_name = 'squalaetp/modal/log_file.html'

    def get_context_data(self, **kwargs):
        context = super(LogFileView, self).get_context_data(**kwargs)
        file = LogFile(os.path.join(CSD_ROOT, 'LOGS'), )
        xelon = get_object_or_404(Xelon, pk=context['pk'])
        if xelon.corvet:
            if xelon.corvet.electronique_14x:
                btel = Multimedia.objects.filter(hw_reference=xelon.corvet.electronique_14x).first()
                text = file.vin_err_filter(btel.name, xelon.numero_de_dossier)
                # print(f"Info LOG : {btel.name} - {xelon.numero_de_dossier}")
                context['text'] = text
        return context
