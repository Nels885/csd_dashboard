from io import StringIO

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDictKeyError
from django.core.management import call_command

from reman.models import Batch, Repair, EcuModel
from .forms import ExportCorvetForm, ExportRemanForm, ExportCorvetVinListForm
from .utils import extract_ecu, extract_corvet
from utils.file.export import ExportExcel
from utils.file import handle_uploaded_file
from pandas.errors import ParserError

context = {
    'title': 'Import / Export'
}


@login_required()
def import_export(request):
    """ View of import/export files page """
    table_title = 'Import Export'
    form_corvet = ExportCorvetForm()
    form_corvet_vin = ExportCorvetVinListForm()
    form_reman = ExportRemanForm()
    context.update(locals())
    return render(request, 'import_export/import_export.html', context)


def export_corvet(request):
    if request.user.has_perm('squalaetp.view_corvet') and request.POST:
        if "btn_corvet_vin" in request.POST:
            form = ExportCorvetVinListForm(request.POST or None)
            if form.is_valid():
                vin_list = form.cleaned_data['vin_list'].split('\r\n')
                return extract_ecu(vin_list)
        elif "btn_corvet_all" in request.POST:
            form = ExportCorvetForm(request.POST or None)
            if form.is_valid():
                product = form.cleaned_data['products']
                excel_type = form.cleaned_data['formats']
                if product in ['corvet', 'ecu', 'bsi', 'com200x', 'bsm']:
                    return extract_corvet(product, excel_type)
    else:
        messages.warning(request, _('You do not have the required permissions'))
    return redirect(request.META.get('HTTP_REFERER'))


def export_reman(request):
    form = ExportRemanForm(request.POST or None)
    if form.is_valid():
        if request.user.has_perms(['reman.view_batch', 'reman.view_repair', 'reman.view_ecumodel']):
            table = form.cleaned_data['tables']
            if table in ['batch', 'repair', 'base_ref']:
                return redirect('import_export:export_{}_csv'.format(table))
        messages.warning(request, _('You do not have the required permissions'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('reman.view_batch')
def export_batch_csv(request):
    filename = 'batch_reman'
    header = [
        'Numero de lot', 'Quantite', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Date_de_Debut',
        'Date_de_fin', 'Actif', 'Ajoute par', 'Ajoute le'
    ]
    batch = Batch.objects.all().order_by('batch_number')
    values_list = (
        'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'ecu_ref_base__ecu_type__technical_data',
        'ecu_ref_base__ecu_type__hw_reference', 'ecu_ref_base__ecu_type__supplier_oe', 'start_date', 'end_date',
        'active', 'created_by__username', 'created_at'
    )
    return ExportExcel(queryset=batch, filename=filename, header=header, values_list=values_list).http_response()


@permission_required('reman.view_repair')
def export_repair_csv(request):
    filename = 'repair_reman'
    header = [
        'Numero_identification', 'Numero_lot', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'SW_Reference', 'Fabriquant',
        'Remarque', 'Cree_le', 'Modifie_par', 'Date_de_cloture'
    ]
    batch = Repair.objects.all().order_by('identify_number')
    values_list = (
        'identify_number', 'batch__batch_number', 'batch__ecu_ref_base__reman_reference',
        'batch__ecu_ref_base__ecu_type__technical_data', 'batch__ecu_ref_base__ecu_type__hw_reference',
        'batch__ecu_ref_base__ecu_type__ecumodel__sw_reference', 'batch__ecu_ref_base__ecu_type__supplier_oe', 'remark',
        'created_at', 'modified_by__username', 'closing_date'
    )
    return ExportExcel(queryset=batch, filename=filename, header=header, values_list=values_list).http_response()


@permission_required('reman.view_ecumodel')
def export_base_ref_csv(request):
    filename = 'base_ref_reman_new'
    header = [
        'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR', 'REF CAL',
        'REF à créer '
    ]
    ecus = EcuModel.objects.all().order_by('ecu_type__ecu_ref_base__reman_reference')
    values_list = (
        'oe_raw_reference', 'ecu_type__ecu_ref_base__reman_reference', 'ecu_type__technical_data',
        'ecu_type__hw_reference', 'ecu_type__supplier_oe', 'psa_barcode', 'former_oe_reference', 'sw_reference',
        'ecu_type__spare_part__code_produit'
    )
    return ExportExcel(
        queryset=ecus, filename=filename, header=header, values_list=values_list, excel_type='xls').http_response()


@permission_required('reman.add_sparepart', 'reman.change_sparepart')
def import_sparepart(request):
    if request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                out = StringIO()
                call_command("spareparts", "--file", file_url, stdout=out)
                for msg in out.getvalue().split("\n"):
                    messages.success(request, msg)
                # messages.success(request, 'Upload terminé !')
                return redirect('reman:part_table')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except (UnicodeDecodeError, ParserError):
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    return redirect('import_export:detail')


@permission_required('reman.add_ecumodel', 'reman.change_ecumodel')
def import_ecureference(request):
    if request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                out = StringIO()
                call_command("ecureference", "--file", file_url, stdout=out)
                for msg in out.getvalue().split("\n"):
                    messages.success(request, msg)
                # messages.success(request, 'Upload terminé !')
                return redirect('reman:ecu_table')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except UnicodeDecodeError:
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    return redirect('import_export:detail')


@permission_required('reman.add_ecurefbase', 'reman.change_ecurefbase')
def import_ecurefbase(request):
    if request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                out = StringIO()
                call_command("ecurefbase", "--sheet_id", 1, "--file", file_url, stdout=out)
                for msg in out.getvalue().split("\n"):
                    messages.success(request, msg)
                # messages.success(request, 'Upload terminé !')
                return redirect('reman:ecu_table')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except UnicodeDecodeError:
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    return redirect('import_export:detail')
