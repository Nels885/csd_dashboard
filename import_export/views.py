from io import StringIO

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDictKeyError
from django.core.management import call_command
from django.http import JsonResponse, Http404

from .forms import ExportCorvetForm, ExportRemanForm, CorvetVinListForm, ExportToolsForm
from utils.file import handle_uploaded_file
from pandas.errors import ParserError
from .tasks import export_corvet_task, export_reman_task, export_tools_task
from psa.tasks import import_corvet_list_task

context = {
    'title': 'Extraction'
}


@login_required()
def import_export(request):
    """ View of import/export files page """
    form_corvet = ExportCorvetForm()
    form_corvet_vin = CorvetVinListForm()
    form_reman = ExportRemanForm()
    form_tools = ExportToolsForm()
    context.update(locals())
    return render(request, 'import_export/import_export.html', context)


def import_sparepart(request):
    if request.user.has_perms(['reman.add_sparepart', 'reman.change_sparepart']) and request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                out = StringIO()
                call_command("loadsparepart", "--file", file_url, stdout=out)
                for msg in out.getvalue().split("\n"):
                    messages.success(request, msg)
                # messages.success(request, 'Upload terminé !')
                return redirect('squalaetp:stock_parts')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except (UnicodeDecodeError, ParserError):
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    else:
        messages.warning(request, _('You do not have the required permissions'))
    return redirect('import_export:detail')


def import_ecurefbase(request):
    if request.user.has_perms(['reman.add_ecurefbase', 'reman.change_ecurefbase']) and request.method == 'POST':
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
    else:
        messages.warning(request, _('You do not have the required permissions'))
    return redirect('import_export:detail')


def export_corvet_async(request):
    form = ExportCorvetForm(request.POST or None)
    if form.is_valid():
        value_dict = {
            'product': form.cleaned_data['product'], 'cols': form.cleaned_data['columns'],
            'start_date': form.cleaned_data['start_date'], 'end_date': form.cleaned_data['end_date'],
            'excel_type': form.cleaned_data['formats']
        }
        task = export_corvet_task.delay(**value_dict)
        return JsonResponse({"task_id": task.id})
    raise Http404


def export_corvet_vin_async(request):
    form = CorvetVinListForm(request.POST or None)
    if form.is_valid():
        vin_list = form.cleaned_data['vin_list'].split('\r\n')
        task = export_corvet_task.delay(vin_list=vin_list)
        return JsonResponse({"task_id": task.id})
    raise Http404


def import_corvet_vin_async(request):
    form = CorvetVinListForm(request.POST or None)
    if form.is_valid():
        vin_list = form.cleaned_data['vin_list'].split('\r\n')
        task = import_corvet_list_task.delay(*vin_list)
        return JsonResponse({"task_id": task.id})
    raise Http404


def export_reman_async(request):
    form = ExportRemanForm(request.POST or None)
    if form.is_valid():
        table = form.cleaned_data['tables']
        excel_type = form.cleaned_data['formats']
        task = export_reman_task.delay(table=table, excel_type=excel_type)
        return JsonResponse({"task_id": task.id})
    raise Http404


def export_tools_async(request):
    form = ExportToolsForm(request.POST or None)
    if form.is_valid():
        table = form.cleaned_data['tables']
        excel_type = form.cleaned_data['formats']
        task = export_tools_task.delay(table=table, excel_type=excel_type)
        return JsonResponse({"task_id": task.id})
    raise Http404
