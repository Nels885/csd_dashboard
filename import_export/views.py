from io import StringIO

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDictKeyError
from django.core.management import call_command

from .forms import ExportCorvetForm, ExportRemanForm, ExportCorvetVinListForm
from .utils import extract_ecu, extract_corvet, extract_reman
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
    if request.user.has_perm('psa.view_corvet') and request.POST:
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
                return extract_corvet(product, excel_type)
    else:
        messages.warning(request, _('You do not have the required permissions'))
    return redirect('import_export:detail')


def export_reman(request):
    if request.user.has_perms(['reman.view_batch', 'reman.view_repair', 'reman.view_ecumodel']) and request.POST:
        form = ExportRemanForm(request.POST or None)
        if form.is_valid():
            table = form.cleaned_data['tables']
            excel_type = form.cleaned_data['formats']
            return extract_reman(table, excel_type)
    else:
        messages.warning(request, _('You do not have the required permissions'))
    return redirect('import_export:detail')


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
