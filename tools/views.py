from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, UpdateView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView
from django.utils import timezone
from constance import config

from .models import CsdSoftware, ThermalChamber, TagXelon, Suptech, SuptechItem, BgaTime
from dashboard.forms import ParaErrorList
from .forms import TagXelonForm, SoftwareForm, ThermalFrom, SuptechModalForm, SuptechResponseForm
from utils.data.mqtt import MQTTClass

MQTT_CLIENT = MQTTClass()


@login_required
def soft_list(request):
    """ View of Software list page """
    title = 'Software'
    table_title = _('Software list')
    softs = CsdSoftware.objects.all()
    return render(request, 'tools/soft_table.html', locals())


@login_required
def tag_xelon_list(request):
    """ View of Software list page """
    title = _('Tools')
    table_title = _('Tag Xelon list')
    tags = TagXelon.objects.all().order_by('-created_at')
    return render(request, 'tools/tag_xelon_table.html', locals())


@permission_required('tools.add_csdsoftware')
def soft_add(request):
    """ View for adding a software in the list """
    title = 'Software'
    card_title = _('Software integration')
    form = SoftwareForm(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        jig = form.cleaned_data['jig']
        ref = CsdSoftware.objects.filter(jig=jig)
        if not ref.exists():
            CsdSoftware.objects.create(**form.cleaned_data)
            messages.success(request, _('Added successfully!'))
            return redirect("tools:soft_list")
    errors = form.errors.items()
    return render(request, 'tools/soft_add.html', locals())


@permission_required('tools.change_csdsoftware')
def soft_edit(request, soft_id):
    """
    View for changing software data
    :param soft_id:
        Software id to edit
    """
    title = 'Software'
    soft = get_object_or_404(CsdSoftware, pk=soft_id)
    card_title = _('Modification data Software for JIG: {jig}'.format(jig=soft.jig))
    form = SoftwareForm(request.POST or None, instance=soft)
    if form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect("tools:soft_list")
    return render(request, 'tools/soft_edit.html', locals())


def thermal_chamber(request):
    title = _('Thermal chamber')
    table_title = _('Use of the thermal chamber')
    now = timezone.now()
    ThermalChamber.objects.filter(created_at__lt=now.date(), active=True).update(active=False)
    thermals = ThermalChamber.objects.filter(active=True).order_by('created_at')
    temp = None
    form = ThermalFrom(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        if request.user.is_authenticated:
            form.save()
            messages.success(request, _('Modification done successfully!'))
        else:
            messages.warning(request, _('You do not have the required permissions'))
    errors = form.errors.items()
    return render(request, 'tools/thermal_chamber.html', locals())


def ajax_temp(request):
    data = MQTT_CLIENT.result()
    return JsonResponse(data)


class ThermalFullScreenView(TemplateView):
    template_name = 'tools/thermal_chamber_fullscreen.html'


class ThermalChamberList(LoginRequiredMixin, ListView):
    queryset = ThermalChamber.objects.all().order_by('-created_at')
    context_object_name = 'thermal_list'
    template_name = 'tools/thermal_chamber_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Thermal chamber')
        context['table_title'] = _('Thermal chamber list')
        return context


@login_required
def thermal_disable(request, pk):
    therm = get_object_or_404(ThermalChamber, pk=pk, active=True)
    if therm.start_time and not therm.stop_time:
        therm.stop_time = timezone.now()
    therm.active = False
    therm.save()
    messages.success(request, 'Suppression réalisé avec succès!')
    return redirect('tools:thermal')


class TagXelonCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'tools.add_tagxelon'
    template_name = 'tools/modal/tag_xelon.html'
    form_class = TagXelonForm
    success_message = 'Success: Création du fichier CALIBRE avec succès !'

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class UltimakerStreamView(LoginRequiredMixin, TemplateView):
    template_name = "tools/ultimaker_stream.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Imprimante 3D"
        context['card_title'] = "Ultimaker Streaming"
        context['stream_url'] = config.PRINTER_STREAM_URL
        return context


class ThermalDeleteView(LoginRequiredMixin, BSModalDeleteView):
    """ View of modal post delete """
    model = ThermalChamber
    template_name = 'tools/modal/thermal_delete.html'
    success_message = _('Success: Input was deleted.')
    success_url = reverse_lazy('tools:thermal')


class SupTechCreateView(BSModalCreateView):
    # permission_required = 'tools.add_suptech'
    template_name = 'tools/modal/suptech_create.html'
    form_class = SuptechModalForm
    success_message = "Succès : Création d'un SupTech avec succès !"

    def form_valid(self, form):
        if not self.request.is_ajax():
            messages.success(self.request, _('Success: The email has been sent.'))
        return super().form_valid(form)

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


def suptech_item_ajax(request):
    data = {"extra": False, "mailing_list": ""}
    try:
        if request.GET.get('pk', None):
            suptech_item = SuptechItem.objects.get(pk=request.GET.get('pk', None))
            data = {"extra": suptech_item.extra, "mailing_list": suptech_item.mailing_list}
    except SuptechItem.DoesNotExist:
        pass
    return JsonResponse(data)


@login_required
def suptech_list(request):
    """ View of Software list page """
    title = _('Support Tech list')
    query_param = request.GET.get('filter', 'all')
    table_title = 'Total'
    objects = Suptech.objects.all().order_by('-date')
    if query_param and query_param == "waiting":
        table_title = 'En Attente'
        objects = objects.filter(status="En Attente")
    elif query_param and query_param == "progress":
        table_title = 'En Cours'
        objects = objects.filter(status="En Cours")
    elif query_param and query_param == "close":
        table_title = 'Cloturées'
        objects = objects.filter(status="Cloturée")
    return render(request, 'tools/suptech/suptech_table.html', locals())


class SuptechResponseView(PermissionRequiredMixin, UpdateView):
    permission_required = 'tools.change_suptech'
    model = Suptech
    form_class = SuptechResponseForm
    template_name = 'tools/suptech/suptech_update.html'
    success_url = reverse_lazy('tools:suptech_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tools"
        context['card_title'] = _("Support Tech Response")
        return context

    def form_valid(self, form):
        if form.send_email(self.request):
            messages.success(self.request, _('Success: The email has been sent.'))
        else:
            messages.warning(self.request, _('Warning: Data update but without sending the email'))
        return super().form_valid(form)


def bga_time(request):
    device = request.GET.get("device", None)
    status = request.GET.get("status", None)
    if device and status:
        try:
            bga_is_active = BgaTime.objects.get(name=device, end_time__isnull=True)
            bga_is_active.save(status=status)
        except BgaTime.DoesNotExist:
            pass
        if status.upper() == "START":
            BgaTime.objects.create(name=device)
        return JsonResponse({"response": "OK", "device": device, "status": status.upper()})
    return JsonResponse({"response": "ERROR"})
