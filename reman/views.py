from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from constance import config
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from utils.django.urls import reverse, reverse_lazy

from utils.conf import string_to_list
from dashboard.forms import ParaErrorList
from .models import Repair, SparePart, Batch, EcuModel, Default, EcuType
from .forms import (
    AddBatchForm, AddRepairForm, EditRepairForm, SparePartFormset, CloseRepairForm, CheckPartForm, DefaultForm,
    PartEcuModelForm, PartEcuTypeForm, PartSparePartForm, EcuModelForm
)

context = {
    'title': 'Reman'
}


@permission_required('reman.view_repair')
def repair_table(request):
    """ View of Reman Repair table page """
    query = request.GET.get('filter')
    if query and query == 'quality':
        files = Repair.objects.filter(quality_control=False)
        table_title = 'Dossiers en cours de réparation'
    elif query and query == 'checkout':
        files = Repair.objects.filter(quality_control=True, checkout=False)
        table_title = "Dossiers en attente d'expédition"
    else:
        files = Repair.objects.all()
        table_title = 'Dossiers de réparation'
    context.update({
        'table_title': table_title,
        'files': files
    })
    return render(request, 'reman/repair_table.html', context)


@permission_required('reman.change_repair')
def out_table(request):
    """ View of Reman Out Repair table page """
    table_title = 'Reman Out'
    files = Repair.objects.filter(quality_control=True, checkout=False)
    form = CloseRepairForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        repair = form.save()
        messages.success(request, _('Adding Repair n°%(repair)s to lot n°%(batch)s successfully') % {
            'repair': repair.identify_number,
            'batch': repair.batch})
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/out_table.html', context)


@permission_required('reman.view_batch')
def batch_table(request):
    """ View of batch table page """
    table_title = 'Liste des lots REMAN ajoutés'
    batchs = Batch.objects.all()
    context.update(locals())
    return render(request, 'reman/batch_table.html', context)


@permission_required('reman.view_sparepart')
def part_table(request):
    """ View of SparePart table page """
    table_title = 'Pièces détachées'
    files = SparePart.objects.all()
    context.update(locals())
    return render(request, 'reman/part_table.html', context)


@permission_required('reman.view_ecurefbase')
def ecu_ref_table(request):
    """ View of EcuRefBase table page """
    table_title = 'Base ECU Reman'
    ecus = EcuModel.objects.all()
    context.update(locals())
    return render(request, 'reman/ecu_ref_base_table.html', context)


@permission_required('reman.view_default')
def default_table(request):
    table_title = 'Liste de panne'
    defaults = Default.objects.all()
    context.update(locals())
    return render(request, 'reman/default_table.html', context)


@permission_required('reman.change_repair')
def edit_repair(request, pk):
    """ View of edit repair page """
    card_title = _('Modification customer folder')
    prod = get_object_or_404(Repair, pk=pk)
    form = EditRepairForm(request.POST or None, instance=prod)
    formset = SparePartFormset(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect(reverse('reman:repair_table', get={'filter': 'quality'}))
    context.update(locals())
    return render(request, 'reman/edit_repair.html', context)


@permission_required('reman.view_ecumodel')
def check_parts(request):
    card_title = "Check Spare Parts"
    form = CheckPartForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        psa_barcode = form.cleaned_data['psa_barcode']
        return redirect(reverse('reman:create_ecu_model', kwargs={'psa_barcode': psa_barcode}))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/check_parts.html', context)


@permission_required('reman.view_ecumodel')
def ecu_model_create(request, psa_barcode):
    card_title = "Ajout Modèle ECU"
    try:
        ecu = EcuModel.objects.get(psa_barcode=psa_barcode)
    except EcuModel.DoesNotExist:
        ecu = None
    form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList)
    form.initial['psa_barcode'] = psa_barcode
    if form.is_valid():
        form.save()
        return redirect(reverse('reman:create_ecu_type', kwargs={'psa_barcode': psa_barcode}))
    context.update(locals())
    return render(request, 'reman/part_detail.html', context)


@permission_required('reman.view_ecumodel')
def ecu_type_create(request, psa_barcode):
    card_title = "Ajout Type ECU"
    try:
        ecu_type = EcuType.objects.get(ecumodel__psa_barcode=psa_barcode)
        form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList, instance=ecu_type)
    except EcuType.DoesNotExist:
        form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        form.save()
        return redirect(reverse('reman:create_spare_part', kwargs={'psa_barcode': psa_barcode}))
    context.update(locals())
    return render(request, 'reman/part_create_form.html', context)


@permission_required('reman.view_ecumodel')
def spare_part_create(request, psa_barcode):
    card_title = "Ajout Pièce détachée"
    ecu_type = get_object_or_404(EcuType, ecumodel__psa_barcode=psa_barcode)
    try:
        part = SparePart.objects.get(ecutype__ecumodel__psa_barcode=psa_barcode)
        form = PartSparePartForm(request.POST or None, error_class=ParaErrorList, instance=part)
    except SparePart.DoesNotExist:
        form = PartSparePartForm(request.POST or None, error_class=ParaErrorList)
        form.initial['code_produit'] = ecu_type.technical_data + " HW" + ecu_type.hw_reference
    if form.is_valid():
        part_obj = form.save()
        ecu_type.spare_part = part_obj
        ecu_type.save()
        ecu = get_object_or_404(EcuModel, psa_barcode=psa_barcode)
        context.update(locals())
        return render(request, 'reman/part_send_email.html', context)
    context.update(locals())
    return render(request, 'reman/part_create_form.html', context)


@permission_required('reman.view_ecumodel')
def new_part_email(request, psa_barcode):
    mail_subject = '[REMAN] Nouveau code barre PSA'
    message = render_to_string('reman/new_psa_barcode_email.html', {
        'ecu': get_object_or_404(EcuModel, psa_barcode=psa_barcode),
    })
    email = EmailMessage(
        mail_subject, message, to=string_to_list(",|;", config.ECU_TO_EMAIL_LIST),
        cc=string_to_list(",|;", config.ECU_CC_EMAIL_LIST)
    )
    email.send()
    messages.success(request, _('Success: The email has been sent.'))
    return redirect("reman:part_check")


def edit_ecu_ref_base(request, psa_barcode):
    card_title = "Edit Modèle ECU"
    next_form = request.GET.get('next')
    ecu = get_object_or_404(EcuModel, psa_barcode=psa_barcode)
    form = EcuModelForm(request.POST or None, error_class=ParaErrorList, instance=ecu)
    context.update(locals())
    return render(request, 'reman/edit_ecu_ref_base.html', context)


class BatchCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/create_batch.html'
    form_class = AddBatchForm
    success_message = _('Success: Batch was created.')
    success_url = reverse_lazy('reman:batch_table')


class RepairCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_repair'
    template_name = 'reman/modal/create_repair.html'
    form_class = AddRepairForm
    success_message = _('Success: Repair was created.')


class DefaultCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'reman.add_default'
    template_name = 'reman/modal/create_default.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was created.')
    success_url = reverse_lazy('reman:default_table')


class DefaultUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal default update """
    model = Default
    permission_required = 'reman.change_default'
    template_name = 'reman/modal/update_default.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was updated.')
    success_url = reverse_lazy('reman:default_table')
