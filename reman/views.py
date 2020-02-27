from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy

from bootstrap_modal_forms.generic import BSModalCreateView

from .models import Repair
from .forms import AddBatchFrom, AddRepairForm
from dashboard.forms import ParaErrorList


def reman_table(request):
    """
    View of Xelon table page
    """
    files = Repair.objects.all()
    context = {
        'title': 'Reman',
        'table_title': 'Dossiers Reman',
        'files': files
    }
    return render(request, 'reman/reman_table.html', context)


@login_required
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
            context = {'title': _('Added successfully!')}
            return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = AddRepairForm()
    context['form'] = form
    return render(request, 'reman/new_folder.html', context)


class BatchCreateView(BSModalCreateView):
    template_name = 'reman/modal/create_batch.html'
    form_class = AddBatchFrom
    success_message = 'Success: Batch was created.'

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')
