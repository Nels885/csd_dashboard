from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.contrib import messages

from bootstrap_modal_forms.generic import BSModalCreateView
from utils.django.urls import reverse, reverse_lazy

from .models import Repair, SparePart, Batch
from .forms import AddBatchFrom, AddRepairForm, EditRepairFrom, SparePartFormset

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
    View of Xelon table page
    """
    files = SparePart.objects.all()
    context.update({
        'table_title': 'Pièces détachées',
        'files': files
    })
    return render(request, 'reman/part_table.html', context)


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

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class RepairCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_repair'
    template_name = 'reman/modal/create_repair.html'
    form_class = AddRepairForm
    success_message = _('Success: Repair was created.')
