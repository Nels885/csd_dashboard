from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.utils.translation import gettext as _
from django.contrib import messages
from bootstrap_modal_forms.generic import BSModalDeleteView
from django.urls import reverse_lazy

from .models import Raspeedi, UnlockProduct
from .forms import RaspeediForm, UnlockForm
from dashboard.forms import ParaErrorList

context = {'title': 'Prog'}


@permission_required('prog.view_raspeedi')
def table(request):
    """
    View of the Raspeedi table page
    :param request:
        Parameters of the request
    :return:
        Raspeedi table page
    """
    table_title = _('Table Products Telematics PSA')
    products = Raspeedi.objects.all().order_by('ref_boitier')
    context.update(locals())
    return render(request, 'prog/table.html', context)


@permission_required('prog.view_raspeedi')
def detail(request, ref_case):
    """
    detailed view of Raspeedi data for a product
    :param ref_case:
        Ref case of product
    """
    prod = get_object_or_404(Raspeedi, ref_boitier=ref_case)
    card_title = _('Detail raspeedi data for the ref case of Product: ') + str(prod.ref_boitier)
    context.update(locals())
    return render(request, 'prog/detail.html', context)


@permission_required('prog.view_unlockproduct')
def unlock_prods(request):
    products = UnlockProduct.objects.filter(active=True).order_by('-created_at')
    table_title = _('Unlocking product for programming')
    form = UnlockForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        if request.user.has_perm('prog.add_unlockproduct'):
            form.save()
            messages.success(
                request, _('Adding the Xelon number %(xelon)s successfully') % {'xelon': form.cleaned_data['unlock']})
            form = UnlockForm(error_class=ParaErrorList)
        else:
            messages.warning(request, _('You do not have the required permissions'))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'prog/unlock_prods.html', context)


@permission_required('prog.view_unlockproduct')
def unlock_table(request):
    """
    View of the Unlock product table page
    :param request:
        Parameters of the request
    :return:
        Unlock product table page
    """
    table_title = _('Unlock product table')
    products = UnlockProduct.objects.all().order_by('-created_at')
    context.update(locals())
    return render(request, 'prog/unlock_table.html', context)


@permission_required('prog.add_raspeedi')
def insert(request):
    card_title = _('RASPEEDI integration')
    form = RaspeediForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        ref_case = form.cleaned_data['ref_boitier']
        ref = Raspeedi.objects.filter(ref_boitier=ref_case)
        if not ref.exists():
            Raspeedi.objects.create(**form.cleaned_data)
            messages.success(request, _('Added successfully!'))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'prog/insert.html', context)


@permission_required('prog.change_raspeedi')
def edit(request, ref_case):
    prod = get_object_or_404(Raspeedi, ref_boitier=ref_case)
    card_title = _('Modification data RASPEEDI for ref case: ') + str(prod.ref_boitier)
    url = 'prog:edit'
    form = RaspeediForm(request.POST or None, instance=prod)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
    context.update(locals())
    return render(request, 'prog/edit.html', context)


class UnlockProductDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    """ View of modal post delete """
    model = UnlockProduct
    permission_required = 'prog.delete_unlockproduct'
    template_name = 'prog/modal/unlock_delete.html'
    success_message = _('Success: Input was deleted.')
    success_url = reverse_lazy('prog:unlock_prods')


@permission_required('prog.view_raspeedi')
def raspeedi_info(request):
    card_title = "Info Raspeedi"
    context.update(locals())
    return render(request, 'prog/raspeedi_info.html', context)