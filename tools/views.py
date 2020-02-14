from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages

from utils.decorators import group_required
from utils.export import calibre_file
from dashboard.models import CsdSoftware, User
from dashboard.forms import SoftwareForm, ParaErrorList


def soft_list(request):
    """
    View of Software list page
    """
    softs = CsdSoftware.objects.all()
    context = {
        'title': 'Software',
        'table_title': _('Software list'),
        'softs': softs,
    }
    return render(request, 'tools/soft_table.html', context)


@login_required
@group_required('cellule')
def soft_add(request):
    """
    View for adding a software in the list
    """
    context = {
        'title': 'Software',
        'card_title': _('Software integration'),
    }
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        form = SoftwareForm(request.POST, error_class=ParaErrorList)
        if form.is_valid():
            jig = form.cleaned_data['jig']
            ref = CsdSoftware.objects.filter(jig=jig)
            if not ref.exists():
                CsdSoftware.objects.create(**form.cleaned_data, created_by=user)
                context = {'title': _('Added successfully!')}
                return render(request, 'dashboard/done.html', context)
        context['errors'] = form.errors.items()
    else:
        form = SoftwareForm()
    context['form'] = form
    return render(request, 'tools/soft_add.html', context)


@login_required
@group_required('cellule')
def soft_edit(request, soft_id):
    """
    View for changing software data
    :param soft_id:
        Software id to edit
    """
    soft = get_object_or_404(CsdSoftware, pk=soft_id)
    form = SoftwareForm(request.POST or None, instance=soft)
    if form.is_valid():
        form.save()
        context = {'title': _('Modification done successfully!')}
        return render(request, 'dashboard/done.html', context)
    context = {
        'title': 'Software',
        'card_title': _('Modification data Software for JIG: {jig}'.format(jig=soft.jig)),
        'url': 'tools:soft-edit',
        'soft': soft,
        'form': form,
    }
    return render(request, 'tools/soft_edit.html', context)


@login_required
@group_required('technician')
def tag_xelon_multi(request):
    if request.method == 'POST':
        xelon = request.POST.get('xelon')
        comments = request.POST.get('comments')
        if calibre_file(comments, xelon, request.user.username):
            messages.success(request, 'Success: Création du fichier CALIBRE avec succès !')
        else:
            messages.warning(request, 'Warning: Le fichier CALIBRE éxiste !')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'tools/modal_form/tag_xelon_multi.html')
