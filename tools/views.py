import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView

from .models import CsdSoftware, User, ThermalChamber
from dashboard.forms import ParaErrorList
from .forms import TagXelonForm, SoftwareForm, ThermalFrom


def soft_list(request):
    """
    View of Software list page
    """
    softs = CsdSoftware.objects.all()
    context = {
        'title': 'Software',
        'table_title': _('Software list'),
        'softs': softs,
    }
    return render(request, 'tools/soft_table.html', context)


@permission_required('tools.add_csdsoftware')
def soft_add(request):
    """
    View for adding a software in the list
    """
    context = {
        'title': 'Software',
        'card_title': _('Software integration'),
    }
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        form = SoftwareForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            jig = form.cleaned_data['jig']
            ref = CsdSoftware.objects.filter(jig=jig)
            if not ref.exists():
                CsdSoftware.objects.create(**form.cleaned_data, created_by=user)
                messages.success(request, _('Added successfully!'))
        context['errors'] = form.errors.items()
    else:
        form = SoftwareForm()
    context['form'] = form
    return render(request, 'tools/soft_add.html', context)


@permission_required('tools.change_csdsoftware')
def soft_edit(request, soft_id):
    """
    View for changing software data
    :param soft_id:
        Software id to edit
    """
    soft = get_object_or_404(CsdSoftware, pk=soft_id)
    form = SoftwareForm(request.POST or None, instance=soft)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
    context = {
        'title': 'Software',
        'card_title': _('Modification data Software for JIG: {jig}'.format(jig=soft.jig)),
        'url': 'tools:soft-edit',
        'soft': soft,
        'form': form,
    }
    return render(request, 'tools/soft_edit.html', context)


@login_required
def thermal_chamber(request):
    thermals = ThermalChamber.objects.filter(active=True).order_by('created_at')
    context = {
        'title': _('Thermal chamber'),
        'table_title': _('Use of the thermal chamber'),
        'thermals': thermals,
        'now': datetime.datetime.now(),
        'temp': None
    }
    if request.method == 'POST':
        form = ThermalFrom(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            form.save()
            messages.success(request, _('Modification done successfully!'))
        context['errors'] = form.errors.items()
    else:
        form = ThermalFrom()
    context['form'] = form
    return render(request, 'tools/thermal_chamber.html', context)


def thermal_fullscreen(request):
    return render(request, 'tools/thermal_chamber_fullscreen.html')


@login_required
def thermal_disable(request, pk):
    therm = get_object_or_404(ThermalChamber, pk=pk)
    therm.active = False
    therm.save()
    messages.success(request, 'Suppression réalisé avec succès!')
    return redirect('tools:thermal')


class TagXelonView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'tools.add_tagxelon'
    template_name = 'tools/modal/tag_xelon.html'
    form_class = TagXelonForm
    success_message = 'Success: Création du fichier CALIBRE avec succès !'

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')
