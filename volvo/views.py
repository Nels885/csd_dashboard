from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import ugettext as _

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from utils.django.urls import reverse_lazy

from .models import SemRefBase, SemType
from .forms import RemanForm, SemTypeForm

context = {
    'title': 'Reman VOLVO'
}


@permission_required('volvo.view_semrefbase')
def reman_ref_table(request):
    """ View of EcuRefBase table page """
    table_title = 'REMAN Référence'
    refs = SemRefBase.objects.all()
    context.update(locals())
    return render(request, 'volvo/reman_ref_table.html', context)


class SemRemanCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'volvo.add_semrefbase'
    template_name = 'volvo/modal/ref_reman_create.html'
    form_class = RemanForm
    success_message = _('Success: Reman reference was created.')
    success_url = reverse_lazy('volvo:reman_ref_table')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = SemRefBase.objects.filter(reman_reference=self.request.GET.get('ref', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['reman_reference']:
                    initial[field] = value
                if field == 'ecu_type_id' and value is not None:
                    initial['asm_reference'] = SemType.objects.get(pk=value).asm_reference
        return initial


class SemRemanUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = SemRefBase
    permission_required = 'volvo.change_semrefbase'
    template_name = 'volvo/modal/ref_reman_update.html'
    form_class = RemanForm
    success_message = _('Success: Reman reference was updated.')
    success_url = reverse_lazy('volvo:reman_ref_table')


@login_required()
def sem_hw_table(request):
    """ View of SemType table page """
    title = "Reman VOLVO"
    table_title = 'Référence Hardware'
    obj = SemType.objects.all()
    return render(request, 'volvo/sem_hw_table.html', locals())


class SemHwCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal SEM Hardware update """
    permission_required = 'volvo.add_semtype'
    template_name = 'volvo/modal/sem_hw_create.html'
    form_class = SemTypeForm
    success_message = _('Success: Reman SEM HW Reference was created.')
    success_url = reverse_lazy('volvo:sem_hw_table')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = SemType.objects.filter(asm_reference=self.request.GET.get('asm', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['asm_reference']:
                    initial[field] = value
        return initial


class SemHwUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal SEM Hardware update """
    model = SemType
    permission_required = 'volvo.change_semtype'
    template_name = 'volvo/modal/sem_hw_update.html'
    form_class = SemTypeForm
    success_message = _('Success: Reman SEM HW Reference was updated.')
    success_url = reverse_lazy('volvo:sem_hw_table')
