import requests
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.utils.translation import gettext as _
from django.contrib import messages
from bootstrap_modal_forms.generic import BSModalDeleteView, BSModalCreateView, BSModalUpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage

from .models import Raspeedi, UnlockProduct, ToolStatus, AET
from prog.models import MbedSoftware
from .forms import RaspeediForm, UnlockForm, ToolStatusForm, AETModalForm, AETSendSoftwareForm, AETAddSoftwareModalForm
from dashboard.forms import ParaErrorList
from utils.django.urls import reverse_lazy, http_referer

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


@permission_required('prog.view_toolstatus')
def tool_info(request):
    table_title = "Info Outils"
    object_list = ToolStatus.objects.all()
    context.update(locals())
    return render(request, 'prog/tool_info.html', context)


def ajax_tool_info(request, pk):
    data = {'pk': pk, 'status': 'Hors ligne', 'version': '', 'status_code': 404}
    try:
        tool = ToolStatus.objects.get(pk=pk)
        response = requests.get(url=tool.api_url, timeout=(0.05, 0.5))
        if response.status_code >= 200 or response.status_code < 300:
            data = response.json()
        data.update({'href': tool.status_url, 'status_code': response.status_code})
    except (requests.exceptions.RequestException, ToolStatus.DoesNotExist):
        pass
    return JsonResponse(data)


class ToolCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'prog.add_toolstatus'
    template_name = 'prog/modal/tool_create.html'
    form_class = ToolStatusForm
    success_message = "Success: Ajout d'un outil avec succès !"

    def get_success_url(self):
        return http_referer(self.request)


class ToolUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = ToolStatus
    permission_required = 'prog.change_toolstatus'
    template_name = 'prog/modal/tool_update.html'
    form_class = ToolStatusForm
    success_message = "Success: Modification d'un outil avec succès !"

    def get_success_url(self):
        return http_referer(self.request)


def AET_info(request, pk=None):
    title = _('AET')
    card_title = _('AET')
    AET_list = AET.objects.all()
    context.update(locals())
    return render(request, 'prog/aet.html', context)


class AETCreateView(BSModalCreateView):
    template_name = 'prog/modal/aet_create.html'
    form_class = AETModalForm
    success_message = "Succès : Ajout d'un AET avec succès !"

    def get_success_url(self):
        return http_referer(self.request)


class AETUpdateView(BSModalUpdateView):
    model = AET
    template_name = 'prog/modal/aet_update.html'
    form_class = AETModalForm
    success_message = "Success: Modification des infos AET avec succès !"

    def get_success_url(self):
        return http_referer(self.request)


def AETAddSoftwareView(request):
    form = AETAddSoftwareModalForm(request.POST or None, request.FILES or None)
    if form.is_valid() and request.method == "POST":
        request_file = request.FILES['filepath'] if 'filepath' in request.FILES else None
        if request_file:
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            MbedSoftware.objects.create(name=request.POST['name'], version=request.POST['version'],
                                        filepath=fs.url(file))
            success_message = "Success: Modification d'un outil avec succès !"
            context.update(locals())
            AET_info(request)
    else:
        context.update(locals())
        return render(request, 'prog/modal/aet_add_software.html', context)


class AETSendSoftwareView(BSModalCreateView):
    model = AET
    template_name = 'prog/modal/aet_send_software.html'
    form_class = AETSendSoftwareForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['form'] = AETSendSoftwareForm(pk=pk)
        context["modal_title"] = AET.objects.filter(pk=pk).first().name
        return context

    def get_success_url(self):
        return http_referer(self.request)
