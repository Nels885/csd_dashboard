from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.management import call_command

from bootstrap_modal_forms.generic import BSModalCreateView
from utils.django.urls import reverse, reverse_lazy
from utils.file import handle_uploaded_file

from dashboard.forms import ParaErrorList
from .models import Repair, SparePart, Batch, EcuModel
from .forms import AddBatchFrom, AddRepairForm, EditRepairFrom, SparePartFormset, CloseRepairForm
from import_export.forms import ExportCorvetForm, ExportRemanForm

context = {
    'title': 'Reman'
}


@permission_required('reman.view_repair')
def repair_table(request):
    """
    View of Reman Repair table page
    """
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
    """
    View of Reman Out Repair table page
    """
    files = Repair.objects.filter(quality_control=True, checkout=False)
    context.update({
        'table_title': 'Reman Out',
        'files': files,
        'form': CloseRepairForm()
    })
    form = CloseRepairForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        repair = form.save()
        messages.success(request, _('Adding Repair n°%(repair)s to lot n°%(batch)s successfully') % {
            'repair': repair.identify_number,
            'batch': repair.batch})
    context['errors'] = form.errors.items()
    return render(request, 'reman/out_table.html', context)


@permission_required('reman.view_batch')
def batch_table(request):
    batchs = Batch.objects.all()
    context.update({
        'table_title': 'Liste des lots REMAN ajoutés',
        'batchs': batchs
    })
    return render(request, 'reman/batch_table.html', context)


@permission_required('reman.view_sparepart')
def part_table(request):
    """
    View of SparePart table page
    """
    files = SparePart.objects.all()
    context.update({
        'table_title': 'Pièces détachées',
        'files': files
    })
    return render(request, 'reman/part_table.html', context)


@permission_required('reman.view_ecumodel')
def ecu_model_table(request):
    ecus = EcuModel.objects.all()
    context.update({
        'table_title': 'Liste des ECU Cross Référence',
        'ecus': ecus
    })
    return render(request, 'reman/ecu_model_table.html', context)


@permission_required(['squalaetp.add_corvet', 'reman.add_ecumodel', 'reman.change_ecumodel'])
def import_export(request):
    context.update({
        'table_title': 'Import Export',
        'form_corvet': ExportCorvetForm(),
        'form_reman': ExportRemanForm(),
    })
    if request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                call_command("ecureference", "--file", file_url)
                messages.success(request, 'Upload terminé !')
                return redirect('reman:ecu_table')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except UnicodeDecodeError:
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    return render(request, 'reman/import_export.html', context)


@permission_required('reman.change_repair')
def edit_repair(request, pk):
    product = get_object_or_404(Repair, pk=pk)
    form = EditRepairFrom(request.POST or None, instance=product)
    formset = SparePartFormset(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect(reverse('reman:repair_table', get={'filter': 'quality'}))
    context.update({
        'card_title': _('Modification customer folder'),
        'prod': product,
        'form': form,
        'formset': formset
    })
    return render(request, 'reman/edit_repair.html', context)


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
