from io import StringIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView
from django.forms.models import model_to_dict
from django.core.management import call_command

from .models import Xelon, Stock, Action
from psa.models import Corvet
from raspeedi.models import Programing
from reman.models import EcuType
from .forms import IhmForm, VinCorvetModalForm, ProductModalForm, IhmEmailModalForm
from psa.forms import CorvetForm
from dashboard.forms import ParaErrorList
from utils.file import LogFile
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict


@login_required
def update(request, pk):
    out = StringIO()
    call_command("exportsqualaetp", stdout=out)
    if "Export error" in out.getvalue():
        messages.warning(request, "Erreur d'exportation Squalaetp, fichier en lecture seule !!")
    else:
        messages.success(request, "Exportation Squalaetp terminée.")
    return redirect('squalaetp:detail', pk=pk)


@login_required
def xelon_table(request):
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
    stocks = Stock.objects.all()
    return render(request, 'squalaetp/stock_table.html', locals())


@login_required
def detail(request, pk):
    xelon = get_object_or_404(Xelon, pk=pk)
    title = f"{xelon.numero_de_dossier} - {xelon.modele_vehicule} - {xelon.vin}"
    select = "xelon"
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


@permission_required('squalaetp.view_xelon')
def ajax_xelon(request):
    """
    View for changing Xelon data
    """
    pk = request.POST.get('pk')
    file = get_object_or_404(Xelon, pk=pk)
    corvet = Corvet.objects.filter(vin=file.vin).first()
    form = CorvetForm(request.POST or None, instance=corvet, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        # xml_corvet_file(form.cleaned_data['xml_data'], form.cleaned_data['vin'])
        form.save()
        context = {'message': _('Modification done successfully!')}
        messages.success(request, context['message'])
        return JsonResponse(context, status=200)
    print(form.errors)
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


@permission_required('psa.change_corvet')
def ajax_corvet(request):
    """
    View for import CORVET data
    """
    vin = request.GET.get('vin')
    if request.GET and vin:
        out = StringIO()
        call_command("importcorvet", vin, stdout=out)
        data = out.getvalue()
        # data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(vin)
        context = {'xml_data': data}
        return JsonResponse(context, status=200)
    return JsonResponse({"nothing to see": "this isn't happening"}, status=400)


class SqualaetpUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Xelon
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'squalaetp/modal/squalaetp_form.html'
    form_class = VinCorvetModalForm
    success_message = _('Success: Squalaetp data was updated.')

    def get_context_data(self, **kwargs):
        context = super(SqualaetpUpdateView, self).get_context_data(**kwargs)
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
        return super(SqualaetpUpdateView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class ProductUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal product update """
    model = Xelon
    permission_required = ['squalaetp.change_xelon']
    template_name = 'squalaetp/modal/product_update.html'
    form_class = ProductModalForm
    success_message = _('Success: Xelon was updated.')

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        context.update({
            'modal_title': _('Product update for %(file)s' % {'file': self.object.numero_de_dossier})
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
        return super(ProductUpdateView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class VinEmailFormView(PermissionRequiredMixin, BSModalFormView):
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super(VinEmailFormView, self).get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['subject'] = "[{}] Erreur VIN Xelon".format(xelon.numero_de_dossier)
        initial['message'] = self.form_class.vin_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not self.request.is_ajax():
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification VIN effectué."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super(VinEmailFormView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class ProdEmailFormView(PermissionRequiredMixin, BSModalFormView):
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super(ProdEmailFormView, self).get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        initial['subject'] = "[{}] Erreur modèle produit Xelon".format(xelon.numero_de_dossier)
        initial['message'] = self.form_class.prod_message(xelon, self.request)
        return initial

    def form_valid(self, form):
        if not self.request.is_ajax():
            form.send_email()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification modèle Produit effectué."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super(ProdEmailFormView, self).form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class LogFileView(LoginRequiredMixin, TemplateView):
    template_name = 'squalaetp/modal/log_file.html'

    def get_context_data(self, **kwargs):
        context = super(LogFileView, self).get_context_data(**kwargs)
        file = LogFile(CSD_ROOT)
        xelon = get_object_or_404(Xelon, pk=context['pk'])
        text = file.vin_err_filter(xelon.modele_produit, xelon.numero_de_dossier)
        print(f"Info LOG : {xelon.modele_produit} - {xelon.numero_de_dossier}")
        context['text'] = text
        return context
