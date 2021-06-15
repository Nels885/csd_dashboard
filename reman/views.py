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
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from constance import config
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalFormView, BSModalDeleteView
from utils.django.urls import reverse, reverse_lazy

from utils.conf import string_to_list
from utils.django.datatables import QueryTableByArgs
from dashboard.forms import ParaErrorList
from .models import Repair, SparePart, Batch, EcuModel, Default, EcuType, EcuRefBase
from .serializers import RemanRepairSerializer, REPAIR_COLUMN_LIST
from .forms import (
    BatchForm, AddBatchForm, AddRepairForm, EditRepairForm, CloseRepairForm, CheckOutRepairForm, CheckPartForm,
    DefaultForm, PartEcuModelForm, PartEcuTypeForm, PartSparePartForm, EcuModelForm, CheckOutSelectBatchForm,
    EcuDumpModelForm, AddEtudeBatchForm, AddEcuTypeForm, UpdateEcuTypeForm, AddRefRemanForm
)

context = {
    'title': 'Reman'
}

"""
~~~~~~~~~~~~~~~~~
TECHNICIAN VIEWS
~~~~~~~~~~~~~~~~~
"""


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
    return render(request, 'reman/repair/repair_edit.html', context)


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
    return render(request, 'reman/repair/repair_close.html', context)


@permission_required('reman.view_repair')
def repair_detail(request, pk):
    """ View of detail repair page """
    card_title = _('Detail customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = CloseRepairForm(request.POST or None, instance=prod)
    context.update(locals())
    return render(request, 'reman/repair/repair_detail.html', context)


class RepairCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_repair'
    template_name = 'reman/modal/repair_create.html'
    form_class = AddRepairForm
    success_message = _('Success: Repair was created.')


"""
~~~~~~~~~~~~~~
MANAGER VIEWS
~~~~~~~~~~~~~~
"""


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
            return render(request, 'reman/part/part_full_detail.html', context)
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
    return render(request, 'reman/ecu_ref_base_update.html', context)


class BatchCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/batch_create.html'
    form_class = AddBatchForm
    success_message = _('Success: Batch was created.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('Create Batch')
        return context

    def get_success_url(self):
        return reverse_lazy('reman:batch_table', get={'filter': 'pending'})


class BatchEtudeCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/batch_create.html'
    form_class = AddEtudeBatchForm
    success_message = _('Success: Batch was created.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('Create Etude Batch')
        return context

    def get_success_url(self):
        return reverse_lazy('reman:batch_table', get={'filter': 'etude'})


class BatchUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Batch
    permission_required = 'reman.change_batch'
    template_name = 'reman/modal/batch_update.html'
    form_class = BatchForm
    success_message = _('Success: Batch was updated.')

    def form_valid(self, form):
        if form.cleaned_data['number'] > 900:
            self.filter = 'etude'
        else:
            self.filter = 'pending'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reman:batch_table', get={'filter': self.filter})


class BatchDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    model = Batch
    permission_required = 'reman.delete_batch'
    template_name = 'reman/modal/batch_delete.html'
    success_message = _('Success: Batch was deleted.')
    success_url = reverse_lazy('reman:batch_table')


class RefRemanCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'reman.add_ecurefbase'
    template_name = 'reman/modal/ref_reman_create.html'
    form_class = AddRefRemanForm
    success_message = _('Success: Reman reference was created.')
    success_url = reverse_lazy('reman:base_ref_table')


class DefaultCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'reman.add_default'
    template_name = 'reman/modal/default_create.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was created.')
    success_url = reverse_lazy('reman:default_table')


class DefaultUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal default update """
    model = Default
    permission_required = 'reman.change_default'
    template_name = 'reman/modal/default_update.html'
    form_class = DefaultForm
    success_message = _('Success: Reman Default was updated.')
    success_url = reverse_lazy('reman:default_table')


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
        psa_barcode = form.cleaned_data['psa_barcode']
        try:
            ecu = EcuModel.objects.get(psa_barcode=psa_barcode)
            context.update(locals())
            if ecu.ecu_type and ecu.ecu_type.spare_part:
                return render(request, 'reman/part/part_detail.html', context)
        except EcuModel.DoesNotExist:
            pass
        return redirect(reverse('reman:create_ref_base', kwargs={'psa_barcode': psa_barcode}))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/part/part_check.html', context)


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
            return render(request, 'reman/part/part_send_email.html', context)
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
        return redirect(
            reverse('reman:create_ref_base', kwargs={'psa_barcode': psa_barcode}) + '?next=' + str(next_form))
    context.update(locals())
    return render(request, 'reman/part/part_create_form.html', context)


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
    permission_required = 'reman.close_repair'
    template_name = 'reman/modal/batch_select.html'
    form_class = CheckOutSelectBatchForm

    def form_valid(self, form):
        self.filter = '?filter=' + str(form.cleaned_data['batch'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reman:out_table') + self.filter


@permission_required('reman.close_repair')
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
def batch_table(request):
    """ View of batch table page """
    table_title = 'Liste des lots REMAN ajoutés'
    repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
    rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
    packed = Count('repairs', filter=Q(repairs__checkout=True))
    query_param = request.GET.get('filter', None)
    select_tab = 'batch'
    if query_param and query_param == "pending":
        batchs = Batch.objects.filter(active=True, number__lt=900).order_by('end_date')
        select_tab = 'batch_pending'
    elif query_param and query_param == "etude":
        select_tab = 'batch_etude'
        batchs = Batch.objects.filter(number__gte=900).order_by('-end_date')
    else:
        batchs = Batch.objects.filter(number__lt=900).order_by('-created_at')
    batchs = batchs.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
    context.update(locals())
    return render(request, 'reman/batch_table.html', context)


@login_required()
def repair_table(request):
    """ View of Reman Repair table page """
    query_param = request.GET.get('filter')
    select_tab = 'repair'
    if query_param and query_param == 'pending':
        table_title = 'Dossiers en cours de réparation'
        select_tab = 'repair_pending'
    elif query_param and query_param == 'checkout':
        table_title = "Dossiers en attente d'expédition"
    else:
        table_title = 'Dossiers de réparation'
    context.update(locals())
    return render(request, 'reman/repair/ajax_repair_table.html', context)


class RepairViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Repair.objects.all()
    serializer_class = RemanRepairSerializer

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            repair = QueryTableByArgs(self.queryset, REPAIR_COLUMN_LIST, 2, **request.query_params).values()
            serializer = self.serializer_class(repair["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": repair["draw"],
                "recordsTotal": repair["total"],
                "recordsFiltered": repair["count"]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query and query == 'pending':
            self.queryset = self.queryset.exclude(status="Rebut").filter(checkout=False)
        elif query and query == 'checkout':
            self.queryset = self.queryset.filter(status="Réparé", quality_control=True, checkout=False)


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
    table_title = 'REMAN Référence'
    refs = EcuRefBase.objects.all()
    context.update(locals())
    return render(request, 'reman/base_ref_table.html', context)


@login_required()
def ecu_hw_table(request):
    """ View of EcuType table page """
    table_title = 'Référence Hardware'
    ecus = EcuType.objects.all()
    context.update(locals())
    return render(request, 'reman/ecu_hw_table.html', context)


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
    form_class = AddEcuTypeForm
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
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class EcuHwUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = EcuType
    permission_required = 'reman.change_ecutype'
    template_name = 'reman/modal/ecu_hw_update.html'
    form_class = UpdateEcuTypeForm
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
