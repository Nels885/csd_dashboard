from io import StringIO, BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404, FileResponse
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView, BSModalCreateView
from django.forms.models import model_to_dict
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode import code128
from constance import config

from utils.django.datatables import QueryTableByArgs
from .serializers import (
    XelonSerializer, XELON_COLUMN_LIST, SivinSerializer, SIVIN_COLUMN_LIST, SparePartSerializer, SPAREPART_COLUMN_LIST
)
from .models import Xelon, SparePart, Action, Sivin
from .utils import collapse_select
from psa.models import Corvet
from psa.forms import CorvetForm
from psa.templatetags.corvet_tags import get_corvet
from raspeedi.models import Programing
from reman.models import EcuType
from .forms import VinCorvetModalForm, ProductModalForm, IhmEmailModalForm, SivinModalForm
from .tasks import cmd_loadsqualaetp_task
from utils.file import LogFile
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict
from utils.django.urls import reverse_lazy, http_referer


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
    return redirect(http_referer(request))


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
    return Http404


@login_required
def xelon_table(request):
    """ View of Xelon table page """
    title = 'Xelon'
    form = CorvetForm()
    query_param = request.GET.get('filter', '')
    return render(request, 'squalaetp/ajax_xelon_table.html', locals())


@login_required
def stock_table(request):
    """ View of SparePart table page """
    title = 'Xelon'
    table_title = 'Pièces détachées'
    # stocks = SparePart.objects.all()
    return render(request, 'squalaetp/stock_table.html', locals())


class StockViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset, SPAREPART_COLUMN_LIST, 0, **request.query_params).values()
            serializer = self.serializer_class(query["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": query["draw"],
                "recordsTotal": query["total"],
                "recordsFiltered": query["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


@login_required
def detail(request, pk):
    """ Detailed view of the selected Xelon number """
    xelon = get_object_or_404(Xelon, pk=pk)
    corvet = xelon.corvet
    title = xelon.numero_de_dossier
    select = "xelon"
    collapse = collapse_select(xelon)
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
    return render(request, 'squalaetp/detail/detail.html', locals())


def barcode_pdf_generate(request, pk):
    xelon = get_object_or_404(Xelon, pk=pk)
    if xelon.corvet:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setTitle(f"xelon_{xelon.numero_de_dossier}")
        p.setFont('Courier', 15)
        p.setLineWidth(4)
        p.drawString(50, 700, "N° Xelon :")
        p.drawString(50, 600, "V.I.N. :")
        p.line(50, 535, 550, 535)
        p.drawString(50, 500, "Marque :")
        p.drawString(50, 450, "Modèle véhicule :")
        p.drawString(50, 400, "Modèle produit :")
        p.line(50, 355, 550, 355)
        p.drawString(50, 300, "Réf. boitier :")
        p.drawString(50, 200, "Cal. CORVET :")

        p.setFont('Courier-Bold', 15)
        p.drawString(250, 700, str(xelon.numero_de_dossier))
        barcode = code128.Code128(str(xelon.numero_de_dossier), barWidth=0.5 * mm, barHeight=10 * mm)
        barcode.drawOn(p, 200, 660)
        p.drawString(250, 600, str(xelon.vin))
        barcode = code128.Code128(str(xelon.vin), barWidth=0.5 * mm, barHeight=10 * mm)
        barcode.drawOn(p, 170, 560)
        p.drawString(250, 500, str(get_corvet(xelon.corvet.donnee_marque_commerciale, "DON_MAR_COMM")))
        p.drawString(250, 450, str(xelon.modele_vehicule))
        if xelon.corvet.electronique_94x:
            media = xelon.corvet.prods.btel
            hw_ref = xelon.corvet.electronique_14x
            sw_ref = xelon.corvet.electronique_94x
        else:
            media = xelon.corvet.prods.radio
            hw_ref = xelon.corvet.electronique_14f
            sw_ref = xelon.corvet.electronique_94f
        try:
            p.drawString(250, 400, str(media.get_name_display()))
            if media.level:
                p.drawString(400, 400, str(media.level))
        except AttributeError:
            p.drawString(250, 400, str(xelon.modele_produit))
        p.drawString(250, 300, str(hw_ref))
        barcode = code128.Code128(str(hw_ref), barWidth=0.5 * mm, barHeight=10 * mm)
        barcode.drawOn(p, 210, 260)
        p.drawString(250, 200, str(sw_ref))
        barcode = code128.Code128(str(sw_ref), barWidth=0.5 * mm, barHeight=10 * mm)
        barcode.drawOn(p, 210, 160)
        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, filename=f"xelon_{xelon.numero_de_dossier}.pdf")
    messages.warning(request, "Génération fichier PDF impossible !")
    return redirect(http_referer(request))


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
            'active_import': 'true',
            'xelon': self.object,
            'modal_title': _('CORVET update for %(file)s' % {'file': self.object.numero_de_dossier})
        })
        return context

    def form_valid(self, form):
        if not self.request.is_ajax():
            data = form.cleaned_data['xml_data']
            vin = form.cleaned_data['vin']
            if data and vin:
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
        initial['to'] = config.CHANGE_VIN_TO_EMAIL_LIST
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
        initial['to'] = config.CHANGE_PROD_TO_EMAIL_LIST
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
        if not self.request.is_ajax():
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
            xelon = QueryTableByArgs(self.queryset, XELON_COLUMN_LIST, 1, **request.query_params).values()
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
        elif query:
            self.queryset = Xelon.search(query)


@login_required
def sivin_table(request):
    """ View of Sivin table page """
    title = 'Sivin'
    return render(request, 'squalaetp/sivin_table.html', locals())


class SivinViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Sivin.objects.all()
    serializer_class = SivinSerializer

    def list(self, request, **kwargs):
        try:
            sivin = QueryTableByArgs(self.queryset, SIVIN_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(sivin["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": sivin["draw"],
                "recordsTotal": sivin["total"],
                "recordsFiltered": sivin["count"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)


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

    def get_success_url(self):
        if not self.request.is_ajax():
            return reverse_lazy('squaletp:sivin_detail', args=[self.object.pk])
        return http_referer(self.request)
