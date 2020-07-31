from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView
from django.utils import timezone

from .models import CsdSoftware, ThermalChamber
from dashboard.forms import ParaErrorList
from .forms import TagXelonForm, SoftwareForm, ThermalFrom


def soft_list(request):
    """ View of Software list page """
    title = 'Software'
    table_title = _('Software list')
    softs = CsdSoftware.objects.all()
    return render(request, 'tools/soft_table.html', locals())


@permission_required('tools.add_csdsoftware')
def soft_add(request):
    """ View for adding a software in the list """
    title = 'Software'
    card_title = _('Software integration')
    form = SoftwareForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        jig = form.cleaned_data['jig']
        ref = CsdSoftware.objects.filter(jig=jig)
        if not ref.exists():
            CsdSoftware.objects.create(**form.cleaned_data)
            messages.success(request, _('Added successfully!'))
            return redirect("tools:soft_list")
    errors = form.errors.items()
    return render(request, 'tools/soft_add.html', locals())


@permission_required('tools.change_csdsoftware')
def soft_edit(request, soft_id):
    """
    View for changing software data
    :param soft_id:
        Software id to edit
    """
    title = 'Software'
    soft = get_object_or_404(CsdSoftware, pk=soft_id)
    card_title = _('Modification data Software for JIG: {jig}'.format(jig=soft.jig))
    form = SoftwareForm(request.POST or None, instance=soft)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect("tools:soft_list")
    return render(request, 'tools/soft_edit.html', locals())


@login_required
def thermal_chamber(request):
    title = _('Thermal chamber')
    table_title = _('Use of the thermal chamber')
    now = timezone.now()
    ThermalChamber.objects.filter(created_at__lt=now.date(), active=True).update(active=False)
    thermals = ThermalChamber.objects.filter(active=True).order_by('created_at')
    temp = None
    form = ThermalFrom(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
    errors = form.errors.items()
    return render(request, 'tools/thermal_chamber.html', locals())


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
