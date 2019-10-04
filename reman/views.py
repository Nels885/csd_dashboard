from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from .models import Reman
from .forms import AddRemanForm
from dashboard.forms import ParaErrorList


def reman_table(request):
    """
    View of Xelon table page
    """
    files = Reman.objects.all()
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
        form = AddRemanForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            reman = form.save(commit=False)
            reman.user_id = request.user.id
            reman.save()
            context = {'title': _('Added successfully!')}
            return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = AddRemanForm()
    context['form'] = form
    return render(request, 'reman/new_folder.html', context)
