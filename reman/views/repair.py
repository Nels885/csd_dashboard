from . import context

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalFormView
from utils.django.urls import reverse, reverse_lazy

from utils.django.datatables import QueryTableByArgs
from reman.models import Repair, RepairPart
from reman.serializers import RemanRepairSerializer, RemanRepairPartSerializer, REPAIR_COLUMN_LIST
from reman.forms import AddRepairForm, EditRepairForm, CloseRepairForm, RepairPartForm, RepairForm, SelectRepairForm
from reman.tasks import cmd_exportreman_task


"""
~~~~~~~~~~~~~~~~~
TECHNICIAN VIEWS
~~~~~~~~~~~~~~~~~
"""


@permission_required('reman.change_repair')
def repair_edit(request, pk):
    """ View of edit repair page """
    card_title = _('Modification customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = EditRepairForm(request.POST or None, instance=prod)
    form2 = RepairPartForm(request.GET or None)
    if request.POST:
        if "repair_part" not in request.POST and form.is_valid():
            form.save()
            if "btn_repair_close" in request.POST:
                return redirect(reverse('reman:close_repair', kwargs={'pk': prod.pk}))
            messages.success(request, _('Modification done successfully!'))
            cmd_exportreman_task.delay('--repair')
            return redirect(reverse('reman:repair_table', get={'filter': 'pending'}))
    context.update(locals())
    return render(request, 'reman/repair/repair_edit.html', context)


def ajax_repair_part_list(request, pk):
    prod = get_object_or_404(Repair, pk=pk)
    parts = RepairPart.objects.filter(object_id=prod.pk)
    serializer = RemanRepairPartSerializer(parts, many=True)
    return JsonResponse({
        "prod_id": prod.pk, "data": serializer.data
    })


def ajax_repair_part_create(request, pk):
    prod = get_object_or_404(Repair, pk=pk)
    form = RepairPartForm(request.POST or None)
    if request.POST and form.is_valid():
        product_code = form.cleaned_data["product_code"]
        quantity = form.cleaned_data["quantity"]
        part = RepairPart.objects.create(product_code=product_code, quantity=quantity, content_object=prod)
        parts = RepairPart.objects.filter(object_id=prod.pk)
        serializer = RemanRepairPartSerializer(parts, many=True)
        return JsonResponse({
            "prod_id": prod.pk, "part_id": part.pk, "product_code": product_code, "quantity": quantity,
            "data": serializer.data
        })
    return JsonResponse({"errors": form.errors})


def ajax_repair_part_delete(request, pk):
    part = get_object_or_404(RepairPart, pk=pk)
    part.delete()
    parts = RepairPart.objects.filter(object_id=part.object_id)
    serializer = RemanRepairPartSerializer(parts, many=True)
    return JsonResponse({"delete": "OK", "data": serializer.data})


@permission_required('reman.change_repair')
def repair_close(request, pk):
    """ View of close repair page """
    card_title = _('Modification customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = CloseRepairForm(request.POST or None, instance=prod)
    if request.POST and form.is_valid():
        form.save()
        messages.success(request, _('Modification done successfully!'))
        return redirect(reverse('reman:repair_table', get={'filter': 'pending'}))
    context.update(locals())
    return render(request, 'reman/repair/repair_close.html', context)


@permission_required('reman.view_repair')
def repair_detail(request, pk):
    """ View of detail repair page """
    card_title = _('Detail customer file')
    prod = get_object_or_404(Repair, pk=pk)
    form = RepairForm(request.POST or None, instance=prod)
    context.update(locals())
    return render(request, 'reman/repair/repair_detail.html', context)


class RepairCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_repair'
    template_name = 'reman/modal/repair_create.html'
    form_class = AddRepairForm
    success_message = _('Success: Repair was created.')


class RepairSelectView(PermissionRequiredMixin, BSModalFormView):
    permission_required = 'reman.add_repair'
    template_name = 'format/modal_custom_form.html'
    form_class = SelectRepairForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('Repair REMAN')
        context['button_name'] = _('Open')
        return context

    def form_valid(self, form):
        self.query = Repair.objects.get(identify_number=form.cleaned_data['repair'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reman:edit_repair', kwargs={'pk': self.query.pk})


@login_required()
def repair_table(request):
    """ View of Reman Repair table page """
    query_param = request.GET.get('filter')
    select_tab = 'repair'
    if query_param and query_param == 'pending':
        table_title = 'Dossiers en cours de réparation'
        select_tab = 'repair_pending'
    elif query_param and query_param == 'checkout':
        table_title = "Dossiers en attente d'expédition"
    else:
        table_title = 'Dossiers de réparation'
    context.update(locals())
    return render(request, 'reman/repair/ajax_repair_table.html', context)


class RepairViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Repair.objects.all()
    serializer_class = RemanRepairSerializer

    def list(self, request, **kwargs):
        try:
            self._filter(request)
            repair = QueryTableByArgs(self.queryset, REPAIR_COLUMN_LIST, 1, **request.query_params).values()
            serializer = self.serializer_class(repair["items"], many=True)
            data = {
                "data": serializer.data,
                "draw": repair["draw"],
                "recordsTotal": repair["total"],
                "recordsFiltered": repair["count"]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err, status=status.HTTP_404_NOT_FOUND)

    def _filter(self, request):
        query = request.query_params.get('filter', None)
        if query and query == 'pending':
            self.queryset = self.queryset.exclude(status="Rebut").filter(checkout=False)
        elif query and query == 'checkout':
            self.queryset = self.queryset.filter(status="Réparé", quality_control=True, checkout=False)
