from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.contrib import messages

from bootstrap_modal_forms.generic import BSModalCreateView
from utils.django.urls import reverse, reverse_lazy

from .models import Repair, SparePart
from .forms import AddBatchFrom, AddRepairForm, EditRepairFrom, SparePartFormset


@permission_required('reman.view_repair')
def repair_table(request):
    """
    View of Xelon table page
    """
    query = request.GET.get('filter')
    if query and query == 'quality':
        files = Repair.objects.filter(quality_control=False)
    else:
        files = Repair.objects.all()
    context = {
        'title': 'Reman',
        'table_title': 'Dossiers Reman',
        'files': files
    }
    return render(request, 'reman/repair_table.html', context)


@permission_required('reman.view_sparepart')
def part_table(request):
    """
    View of Xelon table page
    """
    files = SparePart.objects.all()
    context = {
        'title': 'Reman',
        'table_title': 'Pièces détachées',
        'files': files
    }
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
    context = {
        'title': 'Reman',
        'card_title': _('Modification customer folder'),
        'prod': product,
        'form': form,
        'formset': formset
    }
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
