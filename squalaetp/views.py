from io import StringIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalFormView
from django.forms.models import model_to_dict
from django.core.management import call_command
from constance import config

from .models import Xelon, Stock, Action
from psa.models import Corvet
from raspeedi.models import Programing
from reman.models import EcuType
from .forms import IhmForm, XelonModalForm, IhmEmailModalForm
from psa.forms import CorvetForm
from dashboard.forms import ParaErrorList
from utils.file import LogFile
from utils.conf import CSD_ROOT, string_to_list
from utils.django.models import defaults_dict


@login_required
def update(request, pk):
    out = StringIO()
    call_command("exportsqualaetp", stdout=out)
    for msg in out.getvalue().split("\n"):
        messages.success(request, msg)
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
    form_class = XelonModalForm

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
            obj, created = Corvet.objects.update_or_create(vin=vin, defaults=defaults)
        return super(SqualaetpUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        call_command("exportsqualaetp")
        return _('Success: Squalaetp data was updated.')

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class IhmEmailFormView(PermissionRequiredMixin, BSModalFormView):
    permission_required = ['squalaetp.change_xelon', 'psa.change_corvet']
    template_name = 'squalaetp/modal/ihm_email_form.html'
    form_class = IhmEmailModalForm

    def get_initial(self):
        initial = super(IhmEmailFormView, self).get_initial()
        xelon = Xelon.objects.get(pk=self.kwargs['pk'])
        action = xelon.actions.filter(content__contains="OLD_VIN").first()
        initial['to'] = config.CHANGE_VIN_TO_EMAIL_LIST
        initial['cc'] = config.VIN_ERROR_TO_EMAIL_LIST
        initial['subject'] = "[{}] Erreur VIN Xelon".format(xelon.numero_de_dossier)
        message = "Bonjour,\n\n"
        message += "Vous trouverez ci-dessous, le nouveau VIN pour le dossier {} :\n".format(xelon.numero_de_dossier)
        if action:
            data = action.content.split('\n')
            message += "- Ancien VIN = {}\n".format(data[0][-17:])
            message += "- Nouveau VIN = {}\n".format(data[1][-17:])
        else:
            message += "\n### NOUVEAU VIN NON DISPONIBLE ###\n"
        message += "\nCordialement\n\n"
        message += "{} {}".format(self.request.user.first_name, self.request.user.last_name)
        initial['message'] = message
        return initial

    def form_valid(self, form):
        if not self.request.is_ajax():
            to = form.cleaned_data['to']
            cc = form.cleaned_data['cc']
            mail_subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = EmailMessage(mail_subject, message, to=string_to_list(to), cc=string_to_list(cc))
            email.send()
            xelon = Xelon.objects.get(pk=self.kwargs['pk'])
            content = "Envoi Email de modification VIN effectué."
            Action.objects.create(content=content, content_object=xelon)
            messages.success(self.request, _('Success: The email has been sent.'))
        return super(IhmEmailFormView, self).form_valid(form)

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
