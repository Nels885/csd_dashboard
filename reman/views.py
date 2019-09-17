from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from raspeedi.models import Raspeedi

from raspeedi.forms import RaspeediForm
from dashboard.forms import ParaErrorList


@login_required
def new_folder(request):
    context = {
        'title': 'Reman',
        'card_title': _('New customer folder'),
    }
    if request.method == 'POST':
        form = RaspeediForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            ref_case = form.cleaned_data['ref_boitier']
            ref = Raspeedi.objects.filter(ref_boitier=ref_case)
            if not ref.exists():
                Raspeedi.objects.create(**form.cleaned_data)
                context = {'title': _('Added successfully!')}
                return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = RaspeediForm()
        form.fields['ref_boitier'].initial = "RE000001"
    context['form'] = form
    return render(request, 'reman/new_folder.html', context)
