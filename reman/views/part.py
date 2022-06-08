from . import context

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse

from constance import config
from utils.django.urls import reverse

from utils.conf import string_to_list
from dashboard.forms import ParaErrorList
from reman.models import SparePart, EcuModel, EcuType
from reman.forms import CheckPartForm, PartEcuModelForm, PartSparePartForm


@login_required()
def part_table(request):
    """ View of SparePart table page """
    table_title = 'Pièces détachées'
    parts = SparePart.objects.all()
    context.update(locals())
    return render(request, 'reman/part/part_table.html', context)


@permission_required('reman.check_ecumodel')
def check_parts(request):
    card_title = "Vérification pièce détachée"
    form = CheckPartForm(request.POST or None, error_class=ParaErrorList)
    if request.POST and form.is_valid():
        barcode = form.cleaned_data['barcode']
        try:
            ecu = EcuModel.objects.get(barcode=barcode)
            context.update(locals())
            if ecu.ecu_type and ecu.ecu_type.spare_part:
                return render(request, 'reman/part/part_detail.html', context)
        except EcuModel.DoesNotExist:
            pass
        return redirect(reverse('reman:part_create', kwargs={'barcode': barcode}))
    errors = form.errors.items()
    context.update(locals())
    return render(request, 'reman/part/part_check.html', context)


@permission_required('reman.check_ecumodel')
def create_part(request, barcode):
    next_form = int(request.GET.get('next', 0))
    if next_form == 1:
        card_title = "Ajout Pièce détachée"
        ecu_type = get_object_or_404(EcuType, ecumodel__barcode=barcode)
        try:
            part = SparePart.objects.get(ecutype__ecumodel__barcode=barcode)
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList, instance=part)
        except SparePart.DoesNotExist:
            form = PartSparePartForm(request.POST or None, error_class=ParaErrorList)
            form.initial['code_produit'] = f"{ecu_type.technical_data} HW {ecu_type.hw_reference}"
        if request.POST and form.is_valid():
            part_obj = form.save()
            ecu_type.spare_part = part_obj
            ecu_type.save()
            ecu = get_object_or_404(EcuModel, barcode=barcode)
            context.update(locals())
            return render(request, 'reman/part/part_send_email.html', context)
    else:
        card_title = "Ajout Modèle ECU"
        try:
            instance = EcuModel.objects.get(barcode=barcode)
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList, instance=instance)
            if instance.ecu_type:
                form.initial['hw_reference'] = instance.ecu_type.hw_reference
        except EcuModel.DoesNotExist:
            form = PartEcuModelForm(request.POST or None, error_class=ParaErrorList)
            form.initial['barcode'] = barcode
        if request.POST and form.is_valid():
            form.save()
            return redirect(reverse('reman:part_create', kwargs={'barcode': barcode}) + '?next=1')
    context.update(locals())
    return render(request, 'reman/part/part_create_form.html', context)


def ecu_type_ajax(request):
    data = {"technical_data": "", "supplier_oe": ""}
    try:
        if request.GET.get('hw', None):
            ecu = EcuType.objects.get(hw_reference=request.GET.get('hw', None))
            data = {"technical_data": ecu.technical_data, "supplier_oe": ecu.supplier_oe}
    except EcuType.DoesNotExist:
        pass
    return JsonResponse(data)


@permission_required('reman.check_ecumodel')
def new_part_email(request, barcode):
    mail_subject = '[REMAN] Nouveau code barre PSA'
    ecu = get_object_or_404(EcuModel, barcode=barcode)
    ecu.to_dump = True
    ecu.save()
    message = render_to_string('reman/new_barcode_email.html', {
        'ecu': ecu,
    })
    email = EmailMessage(
        mail_subject, message, to=string_to_list(config.ECU_TO_EMAIL_LIST),
        cc=string_to_list(config.ECU_CC_EMAIL_LIST)
    )
    email.send()
    messages.success(request, _('Success: The email has been sent.'))
    return redirect("reman:part_check")
