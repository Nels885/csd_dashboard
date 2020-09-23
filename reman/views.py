from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models import Max

from constance import config
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from utils.django.urls import reverse, reverse_lazy

from utils.conf import string_to_list
from dashboard.forms import ParaErrorList
from .models import Repair, SparePart, Batch, EcuModel, Default, EcuType
from .forms import (
    AddBatchForm, AddRepairForm, EditRepairForm, CloseRepairForm, CheckOutRepairForm, CheckPartForm,
    DefaultForm, PartEcuModelForm, PartEcuTypeForm, PartSparePartForm, EcuModelForm
)

context = {
    'title': 'Reman'
}


@login_required()
def repair_table(request):
    """ View of Reman Repair table page """
    query = request.GET.get('filter')
    select_tab = 'repair'
    if query and query == 'pending':
        files = Repair.objects.filter(status__exact="En cours")
        table_title = 'Dossiers en cours de réparation'
        select_tab = 'repair_pending'
    elif query and query == 'checkout':
        files = Repair.objects.filter(status="Réparé", quality_control=True, checkout=False)
        table_title = "Dossiers en attente d'expédition"
    else:
        files = Repair.objects.all()
        table_title = 'Dossiers de réparation'
    context.update({
        'table_title': table_title,
        'files': files,
        'select_tab': select_tab
    })
    return render(request, 'reman/repair_table.html', context)


@permission_required('reman.close_repair')
def out_table(request):
    """ View of Reman Out Repair table page """
    table_title = 'Expédition'
    files = Repair.objects.filter(status="Réparé", quality_control=True, checkout=False)
    form = CheckOutRepairForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        repair = form.save()
        messages.success(request, _('Repair n°%(repair)s to batch n°%(batch)s ready for shipment') % {
            'repair': repair.identify_number,
            'batch': repair.batch})
        form = CheckOutRepairForm(error_class=ParaErrorList)
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/out_table.html', context)


@login_required()
def batch_table(request):
    """ View of batch table page """
    table_title = 'Liste des lots REMAN ajoutés'
    batchs = Batch.objects.all()
    context.update(locals())
    return render(request, 'reman/batch_table.html', context)


@login_required()
def part_table(request):
    """ View of SparePart table page """
    table_title = 'Pièces détachées'
    parts = SparePart.objects.all()
    context.update(locals())
    return render(request, 'reman/part_table.html', context)


@permission_required('reman.view_ecurefbase')
def ecu_ref_table(request):
    """ View of EcuRefBase table page """
    table_title = 'Base ECU Reman'
    ecus = EcuModel.objects.all()
    context.update(locals())
    return render(request, 'reman/ecu_ref_base_table.html', context)


@permission_required('reman.view_ecurefbase')
def ecu_dump_table(request):
    table_title = 'Dump à réaliser'
    ecus = EcuModel.objects.filter(to_dump=True)
    context.update(locals())
    return render(request, 'reman/ecu_dump_table.html', context)


@permission_required('reman.view_default')
def default_table(request):
    table_title = 'Liste de panne'
    defaults = Default.objects.all()
    context.update(locals())
    return render(request, 'reman/default_table.html', context)


@permission_required('reman.change_repair')
def repair_edit(request, pk):
    """ View of edit repair page """
    card_title = _('Modification customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = EditRepairForm(request.POST or None, instance=prod)
    if request.POST and form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        if "btn_repair_close" in request.POST:
            return redirect(reverse('reman:close_repair', kwargs={'pk': prod.pk}))
        return redirect(reverse('reman:repair_table', get={'filter': 'pending'}))
    context.update(locals())
    return render(request, 'reman/edit_repair.html', context)


@permission_required('reman.change_repair')
def repair_close(request, pk):
    """ View of close repair page """
    card_title = _('Modification customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = CloseRepairForm(request.POST or None, instance=prod)
    if request.POST and form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect(reverse('reman:repair_table', get={'filter': 'pending'}))
    context.update(locals())
    return render(request, 'reman/close_repair.html', context)


@permission_required('reman.check_ecumodel')
def check_parts(request):
    card_title = "Vérification pièce détachée"
    form = CheckPartForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        psa_barcode = form.cleaned_data['psa_barcode']
        try:
            ecu = EcuModel.objects.get(psa_barcode=psa_barcode)
            context.update(locals())
            if ecu.ecu_type and ecu.ecu_type.spare_part:
                return render(request, 'reman/part_detail.html', context)
        except EcuModel.DoesNotExist:
            pass
        return redirect(reverse('reman:create_ref_base', kwargs={'psa_barcode': psa_barcode}))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/check_parts.html', context)


@permission_required('reman.check_ecumodel')
def new_part_email(request, psa_barcode):
    mail_subject = '[REMAN] Nouveau code barre PSA'
    ecu = get_object_or_404(EcuModel, psa_barcode=psa_barcode)
    ecu.to_dump = True
    ecu.save()
    message = render_to_string('reman/new_psa_barcode_email.html', {
        'ecu': ecu,
    })
    email = EmailMessage(
        mail_subject, message, to=string_to_list(",|;", config.ECU_TO_EMAIL_LIST),
        cc=string_to_list(",|;", config.ECU_CC_EMAIL_LIST)
    )
    email.send()
    messages.success(request, _('Success: The email has been sent.'))
    return redirect("reman:part_check")


@permission_required('reman.add_ecumodel')
def ref_base_create(request, psa_barcode):
    next_form = int(request.GET.get('next', 0))
    if next_form == 1:
        card_title = "Ajout Type ECU"
        try:
            ecu_type = EcuType.objects.get(ecumodel__psa_barcode=psa_barcode)
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList, instance=ecu_type)
        except EcuType.DoesNotExist:
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList)
    elif next_form == 2:
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
    else:
        card_title = "Ajout Modèle ECU"
        try:
            instance = EcuModel.objects.get(psa_barcode=psa_barcode)
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList, instance=instance)
            if instance.ecu_type:
                form.initial['hw_reference'] = instance.ecu_type.hw_reference
        except EcuModel.DoesNotExist:
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList)
            form.initial['psa_barcode'] = psa_barcode
    if request.POST and form.is_valid():
        form.save()
        next_form += 1
        return redirect(reverse('reman:create_ref_base', kwargs={'psa_barcode': psa_barcode}) + '?next=' + str(next_form))
    context.update(locals())
    return render(request, 'reman/part_create_form.html', context)


@permission_required('reman.change_ecumodel')
def ref_base_edit(request, psa_barcode):
    next_form = int(request.GET.get('next', 0))
    if next_form == 1:
        card_title = "Edit Type ECU"
        try:
            ecu_type = EcuType.objects.get(ecumodel__psa_barcode=psa_barcode)
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList, instance=ecu_type)
        except EcuType.DoesNotExist:
            form = PartEcuTypeForm(request.POST or None, error_class=ParaErrorList)
    elif next_form == 2:
        card_title = "Edit Pièce détachée"
        ecu_type = get_object_or_404(EcuType, ecumodel__psa_barcode=psa_barcode)
        try:
            part = SparePart.objects.get(ecutype__ecumodel__psa_barcode=psa_barcode)
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList, instance=part)
        except SparePart.DoesNotExist:
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList)
            form.initial['code_produit'] = ecu_type.part_name()
        if form.is_valid():
            part_obj = form.save()
            ecu_type.spare_part = part_obj
            ecu_type.save()
            ecu = get_object_or_404(EcuModel, psa_barcode=psa_barcode)
            context.update(locals())
            return render(request, 'reman/part_full_detail.html', context)
    else:
        card_title = "Edit Modèle ECU"
        model = get_object_or_404(EcuModel, psa_barcode=psa_barcode)
        form = EcuModelForm(request.POST or None, error_class=ParaErrorList, instance=model)
        form.initial['hw_reference'] = model.ecu_type.hw_reference
    if request.POST and form.is_valid():
        form.save()
        next_form += 1
        return redirect(reverse('reman:edit_ref_base', kwargs={'psa_barcode': psa_barcode}) + '?next=' + str(next_form))
    context.update(locals())
    return render(request, 'reman/edit_ecu_ref_base.html', context)


class BatchCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/create_batch.html'
    form_class = AddBatchForm
    success_message = _('Success: Batch was created.')
    success_url = reverse_lazy('reman:batch_table')

    def get_initial(self):
        initial = super(BatchCreateView, self).get_initial()
        try:
            initial['number'] = Batch.objects.aggregate(Max('number'))['number__max'] + 1
        except TypeError:
            initial['number'] = 1
        return initial


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
