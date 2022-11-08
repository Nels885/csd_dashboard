from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, UpdateView, DetailView
from django.views.generic.edit import FormMixin
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView
from django.utils import timezone
from constance import config

from utils.django.datatables import QueryTableByArgs
from .serializers import TagXelonSerializer, TAG_XELON_COLUMN_LIST

from .models import CsdSoftware, ThermalChamber, TagXelon, Suptech, SuptechItem, BgaTime, SuptechMessage, ConfigFile
from dashboard.forms import ParaErrorList
from .forms import (
    TagXelonForm, SoftwareForm, ThermalFrom, SuptechModalForm, SuptechResponseForm, SuptechMessageForm, Partslink24Form,
    ConfigFileForm, SelectConfigForm, EditConfigForm
)
from utils.data.mqtt import MQTTClass
from utils.django.urls import reverse_lazy, http_referer
from api.utils import thermal_chamber_use
from .tasks import partslink24_task

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
    return render(request, 'tools/tag_xelon_table.html', locals())


class TagXelonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TagXelon.objects.all()
    serializer_class = TagXelonSerializer

    def list(self, request, **kwargs):
        try:
            query = QueryTableByArgs(self.queryset,  TAG_XELON_COLUMN_LIST, 1, **request.query_params).values()
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
    thermal_chamber_use()
    thermals = ThermalChamber.objects.filter(active=True).order_by('created_at')
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
        return http_referer(self.request)


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
        return http_referer(self.request)


def suptech_item_ajax(request):
    data = {"extra": False, "mailing_list": "", "cc_mailing_list": ""}
    try:
        if request.GET.get('pk', None):
            suptech_item = SuptechItem.objects.get(pk=request.GET.get('pk', None))
            data = {
                "extra": suptech_item.extra, "mailing_list": suptech_item.mailing_list,
                "cc_mailing_list": suptech_item.cc_mailing_list,
                "is_48h": suptech_item.is_48h
            }
    except SuptechItem.DoesNotExist:
        pass
    return JsonResponse(data)


@login_required
def suptech_list(request):
    """ View of Software list page """
    title = _('Support Tech list')
    status = request.GET.get('filter', 'all')
    table_title = 'Total'
    objects = Suptech.objects.all().order_by('-date')
    if status == "waiting":
        table_title = 'En Attente'
        objects = objects.filter(status="En Attente")
    elif status == "progress":
        table_title = 'En Cours'
        objects = objects.filter(status="En Cours")
    elif status == "close":
        table_title = 'Cloturées'
        objects = objects.filter(status="Cloturée")
    return render(request, 'tools/suptech/suptech_table.html', locals())


class SuptechDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Suptech
    template_name = 'tools/suptech/suptech_detail.html'
    form_class = SuptechMessageForm

    def get_success_url(self):
        from django.urls import reverse
        return reverse('tools:suptech_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tools"
        context['card_title'] = _(f"SUPTECH N°{self.object.pk} - Detail")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        SuptechMessage.objects.create(content=form.cleaned_data['content'], content_object=self.object)
        messages.success(self.request, _('Success: The message has been added.'))
        if form.send_email(self.request, self.object):
            messages.success(self.request, _('Success: The email has been sent.'))
        else:
            messages.warning(self.request, _('Warning: Data update but without sending the email'))
        return super().form_valid(form)


class SuptechResponseView(PermissionRequiredMixin, UpdateView):
    permission_required = 'tools.change_suptech'
    model = Suptech
    form_class = SuptechResponseForm
    template_name = 'tools/suptech/suptech_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tools"
        context['card_title'] = _(f"SUPTECH N°{self.object.pk} - Response")
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


@login_required
def usb_devices(request):
    title = "USB Devices"
    return render(request, 'tools/usb_devices.html', locals())


@login_required
def partlink24(request):
    title = "Partslink24"
    card_title = "Scraping Partslink24"
    form = Partslink24Form(request.POST or None, error_class=ParaErrorList)
    if form.is_valid():
        if request.user.is_authenticated:
            data = partslink24_task(**form.cleaned_data)
            messages.success(request, _('Modification done successfully!'))
            form = Partslink24Form(None, error_class=ParaErrorList)
        else:
            messages.warning(request, _('You do not have the required permissions'))
    errors = form.errors.items()
    return render(request, 'tools/partlink24.html', locals())


@login_required
def config_files(request, pk=None):
    title = _('Tools')
    card_title = _('Config files')
    form = SelectConfigForm(request.POST or None, error_class=ParaErrorList)
    if pk:
        obj = get_object_or_404(ConfigFile, pk=pk)
        form2 = EditConfigForm(request.POST or None, error_class=ParaErrorList, instance=obj)
        if request.POST and form2.is_valid():
            form2.save()
            messages.success(request, _('Success: Editing the config file.'))
            return redirect('tools:config_files')
    elif "btn_select" in request.POST and form.is_valid():
        pk = form.cleaned_data['select']
        if pk != -1:
            messages.success(request, 'Chargement du fichier de config!')
            return redirect('tools:config_edit', pk=pk)
        messages.warning(request, 'Fichier de config non trouvé !')
    return render(request, 'tools/config_files.html', locals())


class ConfigFileCreateView(BSModalCreateView):
    permission_required = 'tools.add_configfile'
    template_name = 'tools/modal/config_file_create.html'
    form_class = ConfigFileForm
    success_message = "Succès : Création d'un fichier de config avec succès !"
    success_url = reverse_lazy('tools:config_files')
