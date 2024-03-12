from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404, FileResponse
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView, BSModalCreateView
from django.forms.models import model_to_dict
from constance import config

from .models import Xelon, Action, Sivin, XelonTemporary, ProductCode
from .forms import (
    VinCorvetModalForm, ProductModalForm, IhmEmailModalForm, SivinModalForm, XelonCloseModalForm,
    XelonTemporaryModalForm
)
from .tasks import cmd_loadsqualaetp_task, cmd_exportsqualaetp_task
from psa.forms import CorvetForm
from psa.utils import collapse_select
from psa.models import Multimedia, Ecu, Corvet
from prog.models import Programing
from reman.models import EcuType
from tools.models import Suptech
from utils.file import LogFile
from utils.file.pdf_generate import CorvetBarcode
from utils.conf import CSD_ROOT
from utils.django import is_ajax
from utils.django.urls import reverse_lazy, http_referer, reverse


@login_required
def generate(request):
    """ Generating squalaetp EXCEL files """
    task = cmd_exportsqualaetp_task.delay()
    url = http_referer(request)
    if '?' in url:
        return redirect(f"{url}&task_id={task.id}")
    return redirect(f"{url}?task_id={task.id}")


@login_required
def prog_activate(request, pk):
    """ Activating a Xelon number for programming """
    xelon = get_object_or_404(Xelon, pk=pk)
    xelon.is_active = True
    xelon.save()
    content = "Activation Programmation (SWAP)."
    Action.objects.create(content=content, content_object=xelon)
    messages.success(request, "Programmation active.")
    return redirect('squalaetp:generate')


def excel_import_async(request):
    if request.user.has_perm('squalaetp.add_xelon'):
        if request.GET.get("report") == "yes":
            task = cmd_loadsqualaetp_task.delay("--tests")
        else:
            task = cmd_loadsqualaetp_task.delay()
        return JsonResponse({"task_id": task.id})
    raise Http404


@login_required
def xelon_table(request):
    """ View of Xelon table page """
    title = 'Xelon'
    form = CorvetForm()
    query_param = request.GET.get('filter', '')
    if query_param and query_param.isdigit():
        media = Multimedia.objects.filter(comp_ref__exact=query_param).first()
        prod = Ecu.objects.filter(comp_ref__exact=query_param).first()
        parts = ProductCode.objects.filter(name__icontains=query_param)
        vehicles = Corvet.get_vehicles(query_param)
    return render(request, 'squalaetp/xelon_table.html', locals())


@login_required
def temporary_table(request):
    """ View of Xelon temporary table page """
    title = 'Xelon'
    table_title = 'Dossiers temporaires'
    object_list = XelonTemporary.objects.filter(is_active=True).order_by('-created_by')
    return render(request, 'squalaetp/temporary_table.html', locals())


class TemporaryCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'squalaetp.add_xelontemporary'
    template_name = 'squalaetp/modal/xelon_temp_create.html'
    form_class = XelonTemporaryModalForm
    success_message = _('Modification done successfully!')
    success_url = reverse_lazy('squalaetp:temporary')


class TemporaryUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for sending email for VIN errors """
    model = XelonTemporary
    permission_required = 'squalaetp.change_xelontemporary'
    template_name = 'squalaetp/modal/xelon_temp_update.html'
    form_class = XelonTemporaryModalForm

    def get_success_url(self):
        return http_referer(self.request)


@login_required
def stock_table(request):
    """ View of SparePart table page """
    title = 'Xelon'
    table_title = 'Pièces détachées'
    # stocks = SparePart.objects.all()
    return render(request, 'squalaetp/stock_table.html', locals())


@login_required
def detail(request, pk):
    """ Detailed view of the selected Xelon number """
    query_param = request.GET.get('filter', 'xelon')
    if query_param == "temp":
        xelon = get_object_or_404(XelonTemporary, pk=pk)
    else:
        xelon = get_object_or_404(Xelon, pk=pk)
    corvet = xelon.corvet
    title = xelon.numero_de_dossier
    suptechs = Suptech.objects.filter(xelon=xelon.numero_de_dossier)
    select = "xelon"
    collapse = collapse_select(xelon.modele_produit)
    if corvet:
        if corvet.electronique_14x.isdigit():
            prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
        if corvet.electronique_14a.isdigit():
            cmm = EcuType.objects.filter(hw_reference=corvet.electronique_14a).first()
        dict_corvet = model_to_dict(corvet)
        if corvet.prods.btel:
            btel_model = f"{corvet.prods.btel.get_name_display()}  {corvet.prods.btel.level} - {corvet.prods.btel.type}"
        select = 'prods'
    if Sivin.objects.filter(codif_vin=xelon.vin):
        dict_sivin = model_to_dict(Sivin.objects.filter(codif_vin=xelon.vin).first())
    select = request.GET.get('select', select)
    task_id = request.GET.get('task_id', "")
    return render(request, 'squalaetp/detail/detail.html', locals())


def barcode_pdf_generate(request, pk):
    query_param = request.GET.get('filter', 'xelon')
    if query_param == "temp":
        xelon = get_object_or_404(XelonTemporary, pk=pk)
    else:
        xelon = get_object_or_404(Xelon, pk=pk)
    data = {
        'xelon_number': xelon.numero_de_dossier, 'vin': xelon.vin, 'xelon_model': xelon.modele_produit,
        'xelon_vehicle': xelon.modele_vehicule, 'corvet': xelon.corvet,
    }
    buffer = CorvetBarcode(**data).result()
    return FileResponse(buffer, filename=f"xelon_{xelon.numero_de_dossier}.pdf")
    # messages.warning(request, "Génération fichier PDF impossible !")
    # return redirect(http_referer(request))


class VinCorvetUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for updating Corvet and VIN data """
    model = Xelon
    permission_required = ['squalaetp.change_vin']
    template_name = 'squalaetp/modal/vin_corvet_update.html'
    form_class = VinCorvetModalForm
    # success_message = _('Success: %(result)s was updated.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_import': 'true',
            'xelon': Xelon.objects.get(pk=self.object.pk),
            'modal_title': _('CORVET update for %(file)s' % {'file': self.object.numero_de_dossier})
        })
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        if not is_ajax(self.request):
            value = "V.I.N."
            if cleaned_data['vin'] and cleaned_data['xml_data']:
                value = "V.I.N. / CORVET"
            messages.success(self.request, _('Success: %(result)s was updated.') % {'result': value})
        return super().form_valid(form)

    # def get_success_message(self, cleaned_data):
    #     value = "V.I.N."
    #     if cleaned_data['vin'] and cleaned_data['xml_data']:
    #         value = "V.I.N. / CORVET"
    #     return self.success_message % dict(cleaned_data, result=value)

    def get_success_url(self):
        if not is_ajax(self.request):
            task = cmd_exportsqualaetp_task.delay()
            print(task.id)
            return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'task_id': task.id, 'select': 'ihm'})
        return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'select': 'ihm'})


class ProductUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for product update """
    model = Xelon
    permission_required = ['squalaetp.change_product']
    template_name = 'squalaetp/modal/product_update.html'
    form_class = ProductModalForm
    success_message = _('Success: Product was updated.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': _('Product update for %(file)s' % {'file': self.object.numero_de_dossier}),
            'corvet': self.object.corvet
        })
        return context

    def get_success_url(self):
        if not is_ajax(self.request):
            task = cmd_exportsqualaetp_task.delay()
            return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'task_id': task.id, 'select': 'ihm'})
        return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'select': 'ihm'})


class XelonCloseView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for product update """
    model = Xelon
    permission_required = ['squalaetp.change_xelon']
    template_name = 'squalaetp/modal/xelon_close.html'
    form_class = XelonCloseModalForm
    success_message = _('Success: Xelon was updated.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'modal_title': self.object.numero_de_dossier})
        return context

    def get_success_url(self):
        return reverse_lazy('dashboard:products', get={'filter': 'late'})


class VinEmailFormView(PermissionRequiredMixin, BSModalFormView):
    """ Modal view for sending email for VIN errors """
    permission_required = ['squalaetp.email_vin']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super().get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['to'] = config.CHANGE_VIN_TO_EMAIL_LIST
        initial['subject'] = f"[{xelon.numero_de_dossier}] {xelon.modele_produit} Erreur VIN Xelon"
        initial['message'] = self.form_class.vin_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not is_ajax(self.request):
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification VIN effectué."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('squalaetp:detail', args=[self.kwargs['pk']], get={'select': 'ihm'})


class ProdEmailFormView(PermissionRequiredMixin, BSModalFormView):
    """ Modal view for  sending email for Product errors """
    permission_required = ['squalaetp.email_product']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super().get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['to'] = config.CHANGE_PROD_TO_EMAIL_LIST
        initial['subject'] = f"[{xelon.numero_de_dossier}] Erreur modèle produit Xelon"
        initial['message'] = self.form_class.prod_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not is_ajax(self.request):
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification modèle Produit effectué."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('squalaetp:detail', args=[self.kwargs['pk']], get={'select': 'ihm'})


class AdmEmailFormView(PermissionRequiredMixin, BSModalFormView):
    """ Modal view for  sending email for Product errors """
    permission_required = ['squalaetp.email_admin']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super().get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['to'] = config.CHANGE_PROD_TO_EMAIL_LIST
        if self.request.GET.get('select') == "prod":
            initial['subject'] = f"RE: [{xelon.numero_de_dossier}] Erreur modèle produit Xelon"
        else:
            initial['subject'] = f"RE: [{xelon.numero_de_dossier}] {xelon.modele_produit} Erreur VIN Xelon"
        initial['message'] = self.form_class.adm_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not is_ajax(self.request):
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            if self.request.GET.get('select') == "prod":
                content = "Le modèle Produit a été modifié dans Xelon."
            else:
                content = "Le VIN a été modifié dans Xelon."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('squalaetp:detail', args=[self.kwargs['pk']], get={'select': 'ihm'})


class LogFileView(LoginRequiredMixin, TemplateView):
    """ Modal view for displaying product log files """
    template_name = 'squalaetp/modal/log_file.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file = LogFile(CSD_ROOT)
        xelon = get_object_or_404(Xelon, pk=context['pk'])
        text = file.vin_err_filter(xelon.modele_produit, xelon.numero_de_dossier)
        # print(f"Info LOG : {xelon.modele_produit} - {xelon.numero_de_dossier}")
        context['text'] = text
        return context


@login_required
def change_redirect(request, pk):
    query = get_object_or_404(Action, pk=pk)
    obj = query.content_object
    if isinstance(obj, XelonTemporary):
        return redirect(reverse('squalaetp:detail', args=[obj.id], get={'filter': 'temp'}))
    return redirect(reverse('squalaetp:detail', args=[obj.id]))


@login_required
def change_table(request):
    """ View of change table page """
    title = 'Xelon'
    table_title = 'Historique des changements Squalaetp'
    actions = Action.objects.all()
    return render(request, 'squalaetp/change_table.html', locals())


@login_required
def sivin_table(request):
    """ View of Sivin table page """
    title = 'Sivin'
    return render(request, 'squalaetp/sivin_table.html', locals())


@login_required
def sivin_detail(request, immat):
    """
    detailed view of Sivin data for a file
    :param immat:
        immat for SIVIN data
    """
    sivin = get_object_or_404(Sivin, immat_siv=immat)
    title = 'Info PSA'
    corvet = sivin.corvet
    if corvet and corvet.electronique_14x.isdigit():
        prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
    if corvet and corvet.electronique_14a.isdigit():
        cmm = EcuType.objects.filter(hw_reference=corvet.electronique_14a).first()
    card_title = _('Detail SIVIN data for the Immat: ') + sivin.immat_siv
    collapse = {
        "media": True, "prog": True, "emf": True, "cmm": True, "display": True, "audio": True, "ecu": True, "bsi": True,
        "cmb": True
    }
    dict_sivin = model_to_dict(sivin)
    select = "sivin"
    return render(request, 'squalaetp/sivin_detail/detail.html', locals())


class SivinCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'squalaetp.add_sivin'
    template_name = 'squalaetp/modal/sivin_form.html'
    form_class = SivinModalForm
    success_message = _('Modification done successfully!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('SIVIN integration')
        return context

    def form_valid(self, form):
        self.object = form.instance
        return super().form_valid(form)

    def get_success_url(self):
        if not is_ajax(self.request):
            return reverse_lazy('squalaetp:sivin_detail', args=[self.object.pk])
        return http_referer(self.request)
