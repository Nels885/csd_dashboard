from io import StringIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView
from django.forms.models import model_to_dict
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from utils.django.datatables import QueryTableByArgs
from .serializers import XelonSerializer, XELON_COLUMN_LIST
from .models import Xelon, SparePart, Action
from .utils import collapse_select
from psa.models import Corvet
from raspeedi.models import Programing
from reman.models import EcuType
from .forms import IhmForm, VinCorvetModalForm, ProductModalForm, IhmEmailModalForm
from .tasks import cmd_loadsqualaetp_task
from psa.forms import CorvetForm
from utils.file import LogFile
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict
from utils.django.urls import reverse_lazy


@login_required
def generate(request):
    """ Generating squalaetp EXCEL files """
    out = StringIO()
    call_command("exportsqualaetp", stdout=out)
    if "Export error" in out.getvalue():
        for msg in out.getvalue().split('\n'):
            if "Export error" in msg:
                messages.warning(request, msg)
    else:
        messages.success(request, "Exportation Squalaetp terminée.")
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return redirect('index')


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
    if request.user.is_staff:
        task = cmd_loadsqualaetp_task.delay()
        # messages.success(request, "Importation Squalaetp en cours...")
        return JsonResponse({"task_id": task.id})
    # if 'HTTP_REFERER' in request.META:
    #     return HttpResponseRedirect(request.META['HTTP_REFERER'])
    # else:
    #     return redirect('index')
    return Http404


@login_required
def xelon_table(request):
    """ View of Xelon table page """
    title = 'Xelon'
    form = CorvetForm()
    query_param = request.GET.get('filter', None)
    if query_param and query_param == "pending":
        table_title = 'Dossiers en cours'
    elif query_param and query_param == "vin-error":
        table_title = 'Dossiers avec erreur de VIN'
    elif query_param and query_param == "corvet-error":
        table_title = 'Dossiers avec erreur CORVET'
    else:
        table_title = 'Dossiers Clients'
    return render(request, 'squalaetp/ajax_xelon_table.html', locals())


@login_required
def stock_table(request):
    """ View of SparePart table page """
    title = 'Xelon'
    table_title = 'Pièces détachées'
    stocks = SparePart.objects.all()
    return render(request, 'squalaetp/stock_table.html', locals())


@login_required
def detail(request, pk):
    """ Detailed view of the selected Xelon number """
    xelon = get_object_or_404(Xelon, pk=pk)
    title = f"{xelon.numero_de_dossier} - {xelon.modele_vehicule} - {xelon.vin}"
    select = "xelon"
    collapse = collapse_select(xelon)
    if xelon.corvet:
        corvet = xelon.corvet
        if corvet.electronique_14x.isdigit():
            prog = Programing.objects.filter(psa_barcode=corvet.electronique_14x).first()
        if corvet.electronique_14a.isdigit():
            cmm = EcuType.objects.filter(hw_reference=corvet.electronique_14a).first()
        dict_corvet = model_to_dict(corvet)
        select = 'prods'
    select = request.GET.get('select', select)
    form = IhmForm(instance=xelon.corvet,
                   initial=model_to_dict(xelon, fields=('vin', 'modele_produit', 'modele_vehicule')))
    return render(request, 'squalaetp/detail/detail.html', locals())


class VinCorvetUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for updating Corvet and VIN data """
    model = Xelon
    permission_required = ['squalaetp.change_vin']
    template_name = 'squalaetp/modal/vin_corvet_update.html'
    form_class = VinCorvetModalForm
    success_message = _('Success: Squalaetp data was updated.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_import': 'false',
            'xelon': self.object,
            'modal_title': _('CORVET update for %(file)s' % {'file': self.object.numero_de_dossier})
        })
        return context

    def form_valid(self, form):
        if not self.request.is_ajax():
            data = form.cleaned_data['xml_data']
            vin = form.cleaned_data['vin']
            defaults = defaults_dict(Corvet, data, 'vin')
            Corvet.objects.update_or_create(vin=vin, defaults=defaults)
            out = StringIO()
            call_command("exportsqualaetp", stdout=out)
            if "Export error" in out.getvalue():
                messages.warning(self.request, "Erreur d'exportation Squalaetp, fichier en lecture seule !!")
            else:
                messages.success(self.request, "Exportation Squalaetp terminée.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'select': 'ihm'})


class ProductUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ Modal view for product update """
    model = Xelon
    permission_required = ['squalaetp.change_product']
    template_name = 'squalaetp/modal/product_update.html'
    form_class = ProductModalForm
    success_message = _('Success: Xelon was updated.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': _('Product update for %(file)s' % {'file': self.object.numero_de_dossier}),
            'corvet': self.object.corvet
        })
        return context

    def form_valid(self, form):
        if not self.request.is_ajax():
            out = StringIO()
            call_command("exportsqualaetp", stdout=out)
            if "Export error" in out.getvalue():
                messages.warning(self.request, "Erreur d'exportation Squalaetp, fichier en lecture seule !!")
            else:
                messages.success(self.request, "Exportation Squalaetp terminée.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('squalaetp:detail', args=[self.object.id], get={'select': 'ihm'})


class VinEmailFormView(PermissionRequiredMixin, BSModalFormView):
    """ Modal view for sending email for VIN errors """
    permission_required = ['squalaetp.email_vin']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super().get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['subject'] = f"[{xelon.numero_de_dossier}] {xelon.modele_produit} Erreur VIN Xelon"
        initial['message'] = self.form_class.vin_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not self.request.is_ajax():
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
        initial['subject'] = f"[{xelon.numero_de_dossier}] Erreur modèle produit Xelon"
        initial['message'] = self.form_class.prod_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not self.request.is_ajax():
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification modèle Produit effectué."
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
        print(f"Info LOG : {xelon.modele_produit} - {xelon.numero_de_dossier}")
        context['text'] = text
        return context


@login_required
def change_table(request):
    """ View of change table page """
    title = 'Xelon'
    table_title = 'Historique des changements Squalaetp'
    actions = Action.objects.all()
    return render(request, 'squalaetp/change_table.html', locals())


class XelonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Xelon.objects.filter(date_retour__isnull=False)
    serializer_class = XelonSerializer

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            xelon = QueryTableByArgs(self.queryset, XELON_COLUMN_LIST, 2, **request.query_params).values()
            serializer = self.serializer_class(xelon["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": xelon["draw"],
                "recordsTotal": xelon["total"],
                "recordsFiltered": xelon["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query and query == 'pending':
            self.queryset = self.queryset.exclude(type_de_cloture__in=['Réparé', 'N/A'])
        elif query and query == "vin-error":
            self.queryset = self.queryset.filter(vin_error=True).order_by('-date_retour')
        elif query and query == "corvet-error":
            self.queryset = self.queryset.filter(
                vin__regex=r'^VF[37]\w{14}$', vin_error=False, corvet__isnull=True).order_by('-date_retour')
