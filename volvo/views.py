from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext as _

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from utils.django.urls import http_referer

from reman.models import EcuRefBase, EcuType
from .forms import RemanForm, SemTypeForm


class SemRemanCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal default create """
    permission_required = 'reman.add_ecurefbase'
    template_name = 'volvo/modal/ref_reman_create.html'
    form_class = RemanForm
    success_message = _('Success: Reman reference was created.')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = EcuRefBase.objects.filter(reman_reference=self.request.GET.get('ref', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['reman_reference']:
                    initial[field] = value
                if field == 'ecu_type_id' and value is not None:
                    initial['hw_reference'] = EcuType.objects.get(pk=value).hw_reference
        return initial

    def get_success_url(self):
        return http_referer(self.request)


class SemRemanUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = EcuRefBase
    permission_required = 'reman.change_ecurefbase'
    template_name = 'volvo/modal/ref_reman_update.html'
    form_class = RemanForm
    success_message = _('Success: Reman reference was updated.')

    def get_success_url(self):
        return http_referer(self.request)


class SemHwCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal ECU Hardware update """
    permission_required = 'reman.add_ecutype'
    template_name = 'reman/modal/ecu_hw_create.html'
    form_class = SemTypeForm
    success_message = _('Success: Reman SEM HW Reference was created.')

    def get_initial(self):
        initial = super().get_initial()
        ecu_dict = EcuType.objects.filter(hw_reference=self.request.GET.get('hw', None)).values().first()
        if ecu_dict:
            for field, value in ecu_dict.items():
                if field not in ['hw_reference']:
                    initial[field] = value
        return initial

    def get_success_url(self):
        return http_referer(self.request)


class SemHwUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal SEM Hardware update """
    model = EcuType
    permission_required = 'reman.change_ecutype'
    template_name = 'volvo/modal/sem_hw_update.html'
    form_class = SemTypeForm
    success_message = _('Success: Reman SEM HW Reference was updated.')

    def get_success_url(self):
        return http_referer(self.request)
