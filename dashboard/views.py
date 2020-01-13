from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils import translation
from django.contrib.admin.models import LogEntry
from django.conf import settings

import re

from utils.product_Analysis import ProductAnalysis
from utils.decorators import group_required
from .models import Post, CsdSoftware, User, UserProfile
from .forms import SoftwareForm, ParaErrorList, UserProfileForm
from squalaetp.models import Xelon


def index(request):
    """
    View of index page
    """
    posts = Post.objects.all().order_by('-timestamp')
    context = {
        'title': _("Dashboard"),
        'prods': ProductAnalysis(),
        'posts': posts
    }
    return render(request, 'dashboard/index.html', context)


def search(request):
    """
    View of search page
    """
    query = request.GET.get('query')
    if query:
        select = request.GET.get('select')
        if re.match(r'^VF\w{15}$', str(query)):
            file = get_object_or_404(Xelon, vin=query)
        else:
            file = get_object_or_404(Xelon, numero_de_dossier=query)
        context = {
            'title': 'Xelon',
            'card_title': _('Detail data for the Xelon file: {file}'.format(file=file.numero_de_dossier)),
            'file': file,
        }
        if select == "xelon":
            return render(request, 'squalaetp/xelon_detail.html', context)
        else:
            return redirect('squalaetp:ihm-detail', file_id=file.id)
    return redirect(request.META.get('HTTP_REFERER'))


def set_language(request, user_language):
    """
    View of language change
    :param user_language:
        Choice of the user's language
    """
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def activity_log(request):
    logs = LogEntry.objects.filter(user_id=request.user.id)
    context = {
        'title': _("Dashboard"),
        'table_title': _('Activity log'),
        'logs': logs,
    }
    return render(request, 'dashboard/activity_log.html', context)


@login_required
def user_profile(request):
    context = {
        'title': 'Software',
        'card_title': _('Software integration'),
    }
    if request.method == 'POST':
        user = get_object_or_404(UserProfile, user=request.user.id)
        form = UserProfileForm(request.POST or None, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        context['errors'] = form.errors.items()
    else:
        form = UserProfileForm()
    context['form'] = form
    return render(request, 'registration/profile.html', context)


@login_required
@group_required('admin')
def register(request):
    context = {
        'title': 'Register',
    }
    return render(request, 'registration/register.html', context)


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
    return render(request, 'dashboard/soft_table.html', context)


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
    return render(request, 'dashboard/soft_add.html', context)


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
        'url': 'dashboard:soft-edit',
        'soft': soft,
        'form': form,
    }
    return render(request, 'dashboard/soft_edit.html', context)


@login_required
@group_required('cellule')
def config_edit(request):

    if request.method == 'POST':
        query = request.POST.get('config')
        with open(settings.CONF_FILE, 'w+') as file:
            file.write(query)

    with open(settings.CONF_FILE, 'r') as file:
        conf = file.read()
    nb_lines = len(open(settings.CONF_FILE, 'r').readlines()) + 1

    context = {
        'title': 'Configuration',
        'card_title': 'Modification du fichier de configuration',
        'config': conf,
        'nb_lines': nb_lines,
    }

    return render(request, 'dashboard/config.html', context)
