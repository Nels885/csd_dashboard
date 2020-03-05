from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.contrib import messages

from bootstrap_modal_forms.generic import BSModalCreateView
from utils.django.decorators import class_view_decorator

from .models import Repair, SparePart
from .forms import AddBatchFrom, AddRepairForm
from dashboard.forms import ParaErrorList


@permission_required('reman.view_repair')
def repair_table(request):
    """
    View of Xelon table page
    """
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


@permission_required('reman.add_repair')
def new_folder(request):
    context = {
        'title': 'Reman',
        'card_title': _('New customer folder'),
    }
    if request.method == 'POST':
        form = AddRepairForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            reman = form.save(commit=False)
            reman.user_id = request.user.id
            reman.save()
            messages.success(request, _('Added successfully!'))
        context['errors'] = form.errors.items()
    else:
        form = AddRepairForm()
    context['form'] = form
    return render(request, 'reman/new_folder.html', context)


@class_view_decorator(permission_required('tools.add_batch'))
class BatchCreateView(BSModalCreateView):
    template_name = 'reman/modal/create_batch.html'
    form_class = AddBatchFrom
    success_message = _('Success: Batch was created.')

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')
