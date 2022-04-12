import re
from io import StringIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.management import call_command
from django.core.mail import EmailMessage
from django.db.models import Q, Count
from django.views.generic.edit import CreateView, UpdateView

from constance import config
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalFormView
from utils.django.urls import reverse, reverse_lazy, http_referer

from utils.conf import string_to_list
from dashboard.forms import ParaErrorList
from reman.models import Repair, SparePart, Batch, EcuModel, Default, EcuType, EcuRefBase
from reman.forms import (
    CheckOutRepairForm, CheckPartForm,
    DefaultForm, PartEcuModelForm, PartEcuTypeForm, PartSparePartForm, EcuModelForm, CheckOutSelectBatchForm,
    StockSelectBatchForm, EcuDumpModelForm, EcuTypeForm, RefRemanForm
)

context = {
    'title': 'Reman'
}

"""
~~~~~~~~~~~~~~
MANAGER VIEWS
~~~~~~~~~~~~~~
"""


@permission_required('reman.change_ecumodel')
def ref_base_edit(request, barcode):
    next_form = int(request.GET.get('next', 0))
    if next_form == 1:
        card_title = "Edit Type ECU"
        try:
            ecu_type = EcuType.objects.get(ecumodel__barcode=barcode)
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList, instance=ecu_type)
        except EcuType.DoesNotExist:
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList)
    elif next_form == 2:
        card_title = "Edit Pièce détachée"
        ecu_type = get_object_or_404(EcuType, ecumodel__barcode=barcode)
        try:
            part = SparePart.objects.get(ecutype__ecumodel__barcode=barcode)
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList, instance=part)
        except SparePart.DoesNotExist:
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList)
            form.initial['code_produit'] = ecu_type.part_name()
        if form.is_valid():
            part_obj = form.save()
            ecu_type.spare_part = part_obj
            ecu_type.save()
            ecu = get_object_or_404(EcuModel, barcode=barcode)
            context.update(locals())
            return render(request, 'reman/part/part_full_detail.html', context)
    else:
        card_title = "Edit Modèle ECU"
        model = get_object_or_404(EcuModel, barcode=barcode)
        form = EcuModelForm(request.POST or None, error_class=ParaErrorList, instance=model)
        form.initial['hw_reference'] = model.ecu_type.hw_reference
    if request.POST and form.is_valid():
        form.save()
        next_form += 1
        return redirect(reverse('reman:edit_ref_base', kwargs={'barcode': barcode}) + '?next=' + str(next_form))
    context.update(locals())
    return render(request, 'reman/ecu_ref_base_update.html', context)


class RefRemanCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'reman.add_ecurefbase'
    template_name = 'reman/modal/ref_reman_create.html'
    form_class = RefRemanForm
    success_message = _('Success: Reman reference was created.')
    success_url = reverse_lazy('reman:base_ref_table')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = EcuRefBase.objects.filter(reman_reference=self.request.GET.get('ref', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['reman_reference']:
                    initial[field] = value
                if field == 'ecu_type_id' and value is not None:
                    initial['hw_reference'] = EcuType.objects.get(pk=value).hw_reference
        return initial


class RefRemanUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = EcuRefBase
    permission_required = 'reman.change_ecurefbase'
    template_name = 'reman/modal/ref_reman_update.html'
    form_class = RefRemanForm
    success_message = _('Success: Reman reference was updated.')
    success_url = reverse_lazy('reman:base_ref_table')


class DefaultCreateView(PermissionRequiredMixin, CreateView):
    """ View of modal default create """
    permission_required = 'reman.add_default'
    template_name = 'reman/default_form.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was created.')
    success_url = reverse_lazy('reman:default_table')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reman"
        context['card_title'] = _('Create Default')
        return context


class DefaultUpdateView(PermissionRequiredMixin, UpdateView):
    """ View of modal default update """
    model = Default
    permission_required = 'reman.change_default'
    template_name = 'reman/default_form.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was updated.')
    success_url = reverse_lazy('reman:default_table')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reman"
        context['card_title'] = _('Update Default')
        return context


"""
~~~~~~~~~~~~~~~~~~
SPARE PARTS VIEWS
~~~~~~~~~~~~~~~~~~
"""


@permission_required('reman.check_ecumodel')
def check_parts(request):
    card_title = "Vérification pièce détachée"
    form = CheckPartForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        barcode = form.cleaned_data['barcode']
        if re.match(r'^89661-\w{5}$', barcode):
            barcode = barcode[:11]
        else:
            barcode = barcode[:10]
        try:
            ecu = EcuModel.objects.get(barcode=barcode)
            context.update(locals())
            if ecu.ecu_type and ecu.ecu_type.spare_part:
                return render(request, 'reman/part/part_detail.html', context)
        except EcuModel.DoesNotExist:
            pass
        return redirect(reverse('reman:part_create', kwargs={'barcode': barcode}))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/part/part_check.html', context)


@permission_required('reman.check_ecumodel')
def create_part(request, barcode):
    next_form = int(request.GET.get('next', 0))
    if next_form == 1:
        card_title = "Ajout Type ECU"
        try:
            ecu_type = EcuType.objects.get(ecumodel__barcode=barcode)
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList, instance=ecu_type)
        except EcuType.DoesNotExist:
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList)
    elif next_form == 2:
        card_title = "Ajout Pièce détachée"
        ecu_type = get_object_or_404(EcuType, ecumodel__barcode=barcode)
        try:
            part = SparePart.objects.get(ecutype__ecumodel__barcode=barcode)
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList, instance=part)
        except SparePart.DoesNotExist:
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList)
            form.initial['code_produit'] = ecu_type.technical_data + " HW" + ecu_type.hw_reference
        if form.is_valid():
            part_obj = form.save()
            ecu_type.spare_part = part_obj
            ecu_type.save()
            ecu = get_object_or_404(EcuModel, barcode=barcode)
            context.update(locals())
            return render(request, 'reman/part/part_send_email.html', context)
    else:
        card_title = "Ajout Modèle ECU"
        try:
            instance = EcuModel.objects.get(barcode=barcode)
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList, instance=instance)
            if instance.ecu_type:
                form.initial['hw_reference'] = instance.ecu_type.hw_reference
        except EcuModel.DoesNotExist:
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList)
            form.initial['barcode'] = barcode
    if request.POST and form.is_valid():
        form.save()
        next_form += 1
        return redirect(
            reverse('reman:part_create', kwargs={'barcode': barcode}) + '?next=' + str(next_form))
    context.update(locals())
    return render(request, 'reman/part/part_create_form.html', context)


@permission_required('reman.check_ecumodel')
def new_part_email(request, barcode):
    mail_subject = '[REMAN] Nouveau code barre PSA'
    ecu = get_object_or_404(EcuModel, barcode=barcode)
    ecu.to_dump = True
    ecu.save()
    message = render_to_string('reman/new_barcode_email.html', {
        'ecu': ecu,
    })
    email = EmailMessage(
        mail_subject, message, to=string_to_list(config.ECU_TO_EMAIL_LIST),
        cc=string_to_list(config.ECU_CC_EMAIL_LIST)
    )
    email.send()
    messages.success(request, _('Success: The email has been sent.'))
    return redirect("reman:part_check")


"""
~~~~~~~~~~~~~~~
IN / OUT VIEWS
~~~~~~~~~~~~~~~
"""


class CheckOutFilterView(PermissionRequiredMixin, BSModalFormView):
    template_name = 'reman/modal/batch_select.html'

    def get_form_class(self):
        select = self.request.GET.get('select', None)
        if select == "stock":
            return StockSelectBatchForm
        return CheckOutSelectBatchForm

    def has_permission(self):
        user = self.request.user
        return user.has_perm('reman.stock_repair') or user.has_perm('reman.close_repair')

    def form_valid(self, form):
        self.filter = '?filter=' + str(form.cleaned_data['batch'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reman:out_table') + self.filter


# @permission_required('reman.close_repair')
@login_required()
def out_table(request):
    """ View of Reman Out Repair table page """
    batch_number = request.GET.get('filter')
    table_title = 'Préparation lot n° {}'.format(batch_number)
    repaired = Count('repairs', filter=Q(repairs__status="Réparé", repairs__quality_control=True))
    packed = Count('repairs', filter=Q(repairs__checkout=True))
    batch = Batch.objects.filter(batch_number=batch_number).annotate(repaired=repaired, packed=packed).first()
    files = Repair.objects.filter(
        batch__batch_number=batch_number, status="Réparé", checkout=False, quality_control=True
    )
    form = CheckOutRepairForm(request.POST or None, error_class=ParaErrorList, batch_number=batch_number, )
    if request.POST and form.is_valid():
        repair = form.save()
        messages.success(request, _('Repair n°%(repair)s to batch n°%(batch)s ready for shipment') % {
            'repair': repair.identify_number,
            'batch': repair.batch})
        form = CheckOutRepairForm(error_class=ParaErrorList)
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/repair/out_table.html', context)


"""
~~~~~~~~~~~~~~~~~
CONSULTING VIEWS
~~~~~~~~~~~~~~~~~
"""


@login_required()
def part_table(request):
    """ View of SparePart table page """
    table_title = 'Pièces détachées'
    parts = SparePart.objects.all()
    context.update(locals())
    return render(request, 'reman/part/part_table.html', context)


@permission_required('reman.view_ecurefbase')
def base_ref_table(request):
    """ View of EcuRefBase table page """
    if request.GET.get('customer', None) == "volvo":
        title = "Reman VOLVO"
        refs = EcuRefBase.objects.filter(brand__in=['VOLVO', 'RENAULT'])
        return render(request, 'reman/ref/sem_ref_table.html', locals())
    title = "Reman PSA"
    refs = EcuRefBase.objects.exclude(brand__in=['VOLVO', 'RENAULT'])
    return render(request, 'reman/ref/base_ref_table.html', locals())


@login_required()
def ecu_hw_table(request):
    """ View of EcuType table page """
    if request.GET.get('customer', None) == "volvo":
        title = "Reman VOLVO"
        ecus = EcuType.objects.filter(technical_data="SEM")
        return render(request, 'reman/ref/sem_hw_table.html', locals())
    title = "Reman PSA"
    table_title = 'Référence Hardware'
    ecus = EcuType.objects.exclude(technical_data="SEM")
    return render(request, 'reman/ref/ecu_hw_table.html', locals())


@login_required
def ecu_hw_generate(request):
    """ Generating Scan IN/OU EXCEL files """
    out = StringIO()
    call_command("exportreman", "--scan_in_out", stdout=out)
    if "Export error" in out.getvalue():
        for msg in out.getvalue().split('\n'):
            if "Export error" in msg:
                messages.warning(request, msg)
    else:
        messages.success(request, "Exportation Scan IN/OUT terminée.")
    return redirect('reman:ecu_hw_table')


class EcuHwCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal ECU Hardware update """
    permission_required = 'reman.add_ecutype'
    template_name = 'reman/modal/ecu_hw_create.html'
    form_class = EcuTypeForm
    success_message = _('Success: Reman ECU HW Reference was created.')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = EcuType.objects.filter(hw_reference=self.request.GET.get('hw', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['hw_reference']:
                    initial[field] = value
        return initial

    def get_success_url(self):
        return http_referer(self.request)


class EcuHwUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = EcuType
    permission_required = 'reman.change_ecutype'
    template_name = 'reman/modal/ecu_hw_update.html'
    form_class = EcuTypeForm
    success_message = _('Success: Reman ECU HW Reference was updated.')
    success_url = reverse_lazy('reman:ecu_hw_table')


@login_required()
def ecu_dump_table(request):
    table_title = 'Dump à réaliser'
    ecus = EcuModel.objects.filter(to_dump=True)
    context.update(locals())
    return render(request, 'reman/ecu_dump_table.html', context)


class EcuDumpUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Dump update """
    model = EcuModel
    permission_required = 'reman.change_ecumodel'
    template_name = 'reman/modal/ecu_dump_update.html'
    form_class = EcuDumpModelForm
    success_message = _('Success: Reman ECU dump was updated.')
    success_url = reverse_lazy('reman:ecu_dump_table')


@permission_required('reman.view_default')
def default_table(request):
    table_title = 'Liste de panne'
    defaults = Default.objects.all()
    context.update(locals())
    return render(request, 'reman/default_table.html', context)
