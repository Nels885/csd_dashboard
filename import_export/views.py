from io import StringIO

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
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


@login_required
def export_csd_async(request):
    form_vin = CorvetVinListForm()
    form = ExportCorvetForm(request.POST or None)
    if request.POST and form.is_valid():
        task = export_corvet_task.delay(**form.cleaned_data)
        return JsonResponse({"task_id": task.id})
    context.update(locals())
    return render(request, 'import_export/detail_csd.html', context)


@login_required
def export_reman_async(request):
    form = ExportRemanForm(request.POST or None)
    if request.POST and form.is_valid():
        task = export_reman_task.delay(**form.cleaned_data)
        return JsonResponse({"task_id": task.id})
    context.update(locals())
    return render(request, 'import_export/detail_reman.html', context)


@login_required
def export_tools_async(request):
    form = ExportToolsForm(request.POST or None)
    if request.POST and form.is_valid():
        task = export_tools_task.delay(**form.cleaned_data)
        return JsonResponse({"task_id": task.id})
    context.update(locals())
    return render(request, 'import_export/detail_tools.html', context)


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
    return redirect('import_export:reman_async')


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
    return redirect('import_export:reman_async')


@login_required
def import_corvet_vin_async(request):
    form = CorvetVinListForm(request.POST or None)
    if form.is_valid():
        vin_list = form.cleaned_data['vin_list'].split('\r\n')
        task = import_corvet_list_task.delay(*vin_list, **form.cleaned_data)
        return JsonResponse({"task_id": task.id})
    raise Http404
