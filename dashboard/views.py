from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils import translation
from django.contrib.admin.models import LogEntry
from django.conf import settings
from django.urls import reverse_lazy

import re

from bootstrap_modal_forms.generic import BSModalLoginView, BSModalCreateView

from utils.analysis import ProductAnalysis
from utils.decorators import group_required
from .models import Post, UserProfile
from .forms import UserProfileForm, CustomAuthenticationForm, CustomUserCreationForm
from squalaetp.models import Xelon


def index(request):
    """
    View of index page
    """
    posts = Post.objects.all().order_by('-timestamp')
    context = {
        'title': _("Acceuil"),
        'posts': posts
    }
    return render(request, 'dashboard/index.html', context)


def charts(request):
    """
    View of charts page
    """
    context = {
        'title': _("Dashboard"),
        'prods': ProductAnalysis(),
    }
    return render(request, 'dashboard/charts.html', context)


def search(request):
    """
    View of search page
    """
    query = request.GET.get('query')
    if query:
        query = query.upper()
        # select = request.GET.get('select')
        if re.match(r'^\w{17}$', str(query)):
            file = get_object_or_404(Xelon, vin=query)
        elif re.match(r'^[A-Z]\d{9}$', str(query)):
            file = get_object_or_404(Xelon, numero_de_dossier=query)
        else:
            return redirect(request.META.get('HTTP_REFERER'))
        return redirect('squalaetp:detail', file_id=file.id)
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
        'title': 'Profile',
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


def class_view_decorator(function_decorator):
    """Convert a function based decorator into a class based decorator usable
    on class based Views.

    Can't subclass the `View` as it breaks inheritance (super in particular),
    so we monkey-patch instead.
    """

    def simple_decorator(view):
        view.dispatch = method_decorator(function_decorator)(view.dispatch)
        return view

    return simple_decorator


class CustomLoginView(BSModalLoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'dashboard/login.html'
    success_message = _('Success: You were successfully logged in.')
    success_url = reverse_lazy('charts')


@class_view_decorator(login_required)
@class_view_decorator(group_required('admin'))
class SignUpView(BSModalCreateView):
    form_class = CustomUserCreationForm
    template_name = 'dashboard/modal_form/signup.html'
    success_message = _('Success: Sign up succeeded. You can now Log in.')
    success_url = reverse_lazy('index')
