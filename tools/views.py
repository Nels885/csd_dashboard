from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView

from utils.django.decorators import group_required, class_view_decorator
from dashboard.models import CsdSoftware, User
from dashboard.forms import SoftwareForm, ParaErrorList
from .forms import TagXelonForm


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


@login_required
@group_required('cellule')
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


@login_required
@group_required('cellule')
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


@class_view_decorator(group_required('tools-admin'))
class TagXelonView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'tools/modal/tag_xelon.html'
    form_class = TagXelonForm
    success_message = 'Success: Création du fichier CALIBRE avec succès !'

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')
