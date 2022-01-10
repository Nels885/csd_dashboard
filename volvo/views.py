from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import ugettext as _

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from utils.django.urls import reverse_lazy

from .models import SemRefBase
from .forms import RemanForm, UpdateRemanForm

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


class SemRemanUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal ECU Hardware update """
    model = SemRefBase
    permission_required = 'volvo.change_semrefbase'
    template_name = 'volvo/modal/ref_reman_update.html'
    form_class = UpdateRemanForm
    success_message = _('Success: Reman reference was updated.')
    success_url = reverse_lazy('volvo:reman_ref_table')
