from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from constance import config
from bootstrap_modal_forms.generic import BSModalCreateView
from utils.django.urls import reverse, reverse_lazy

from utils.conf import string_to_list
from dashboard.forms import ParaErrorList
from .models import Repair, SparePart, Batch, EcuModel
from .forms import AddBatchFrom, AddRepairForm, EditRepairFrom, SparePartFormset, CloseRepairForm, CheckPartForm

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


@permission_required('reman.change_repair')
def edit_repair(request, pk):
    """ View of edit repair page """
    card_title = _('Modification customer folder')
    prod = get_object_or_404(Repair, pk=pk)
    form = EditRepairFrom(request.POST or None, instance=prod)
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
        try:
            ecu = EcuModel.objects.get(psa_barcode=psa_barcode)
        except EcuModel.DoesNotExist:
            ecu = None
            # messages.warning(request, "Ce code barre PSA n'éxiste pas dans la base de données")
        context.update(locals())
        return render(request, 'reman/part_detail.html', context)
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/check_parts.html', context)


@permission_required('reman.view_ecumodel')
def new_part_email(request, psa_barcode):
    mail_subject = '[REMAN] Nouveau code barre PSA'
    message = render_to_string('reman/new_psa_barcode_email.html', {
        'psa_barcode': psa_barcode,
    })
    email = EmailMessage(
        mail_subject, message, to=string_to_list(",|;", config.ECU_TO_EMAIL_LIST),
        cc=string_to_list(",|;", config.ECU_CC_EMAIL_LIST)
    )
    email.send()
    messages.success(request, _('Success: The email has been sent.'))
    return redirect("reman:part_check")


class BatchCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/create_batch.html'
    form_class = AddBatchFrom
    success_message = _('Success: Batch was created.')
    success_url = reverse_lazy('reman:batch_table')


class RepairCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_repair'
    template_name = 'reman/modal/create_repair.html'
    form_class = AddRepairForm
    success_message = _('Success: Repair was created.')
