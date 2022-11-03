from . import context

from io import BytesIO

from django.utils import timezone
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import gettext as _
from django.db.models import Q, Count, Max
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode import code128

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from utils.django.urls import reverse_lazy

from utils.conf import DICT_YEAR
from reman.models import Batch
from reman.forms import BatchForm, AddBatchForm
from reman.utils import batch_pdf_data


class BatchCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'reman.add_batch'
    template_name = 'reman/modal/batch_create.html'
    form_class = AddBatchForm
    success_message = _('Success: Batch was created.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = _('Create Batch')
        return context

    def form_valid(self, form):
        batch_type = form.cleaned_data['type']
        if "ETUDE" in batch_type:
            filter = 'etude'
        elif "REPAIR" in batch_type:
            filter = 'workshop'
        else:
            filter = 'pending'
        self.success_url = reverse_lazy('reman:batch_table', get={'filter': filter})
        return super().form_valid(form)


def batch_type_ajax(request):
    date = timezone.now()
    data = {"number": 1}
    batch_type = request.GET.get('type', None)
    try:
        if "ETUDE" in batch_type:
            data = {"number": 901}
            batchs = Batch.objects.all().exclude(number__lt=900)
        else:
            batchs = Batch.objects.all().exclude(number__gte=900)
        if "VOLVO" in batch_type:
            batchs = batchs.filter(year="V")
        elif "REPAIR" in batch_type:
            batchs = batchs.filter(year="X")
        else:
            batchs = batchs.filter(year=DICT_YEAR.get(date.year))
        data["number"] = batchs.aggregate(Max('number'))['number__max'] + 1
    except TypeError:
        pass
    return JsonResponse(data)


class BatchUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Batch
    permission_required = 'reman.change_batch'
    template_name = 'reman/modal/batch_update.html'
    form_class = BatchForm
    success_message = _('Success: Batch was updated.')

    def get_success_url(self):
        if self.object.number > 900:
            filter = 'etude'
        elif self.object.year == "X":
            filter = 'workshop'
        else:
            filter = 'pending'
        return reverse_lazy('reman:batch_table', get={'filter': filter})


class BatchDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    model = Batch
    permission_required = 'reman.delete_batch'
    template_name = 'reman/modal/batch_delete.html'
    success_message = _('Success: Batch was deleted.')
    success_url = reverse_lazy('reman:batch_table')


@login_required()
def batch_table(request):
    """ View of batch table page """
    table_title = 'Liste des lots REMAN ajoutés'
    repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
    rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
    packed = Count('repairs', filter=Q(repairs__checkout=True))
    query_param = request.GET.get('filter', None)
    select_tab = 'batch'
    if query_param and query_param == "pending":
        batchs = Batch.objects.filter(active=True, number__lt=900).exclude(year="X").order_by('end_date')
        select_tab = 'batch_pending'
    elif query_param and query_param == "etude":
        select_tab = 'batch_etude'
        batchs = Batch.objects.filter(number__gte=900).order_by('-end_date')
    elif query_param and query_param == "workshop":
        select_tab = 'batch_workshop'
        batchs = Batch.objects.filter(year="X").order_by('-end_date')
    else:
        batchs = Batch.objects.filter(number__lt=900).order_by('-created_at')
    batchs = batchs.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
    context.update(locals())
    return render(request, 'reman/batch_table.html', context)


@permission_required('reman.pdfgen_batch')
def batch_pdf_generate(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    reman_reference, part_name = batch_pdf_data(batch)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setTitle(f"batch_{batch.batch_number}")
    p.rotate(90)
    p.setFont('Courier', 24)
    p.setLineWidth(4)
    p.drawString(60, -130, "REFERENCE REMAN :")
    p.drawString(60, -230, "Type boitier : ")
    p.drawString(60, -330, "N° LOT :")
    p.drawString(60, -430, "Quantité carton :")

    p.setFont('Courier-Bold', 36)
    p.drawString(380, -130, str(reman_reference))
    barcode = code128.Code128(str(reman_reference), barWidth=0.5 * mm, barHeight=10 * mm)
    barcode.drawOn(p, 610, -130)
    p.drawString(380, -230, str(part_name))
    p.drawString(380, -330, str(batch.batch_number))
    p.line(470, -340, 530, -340)
    barcode = code128.Code128(str(batch.batch_number), barWidth=0.5 * mm, barHeight=10 * mm)
    barcode.drawOn(p, 610, -330)
    p.drawString(380, -430, str(batch.box_quantity))
    # p.line(380, -440,  400, -440)
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, filename=f"batch_{batch.batch_number}.pdf")
