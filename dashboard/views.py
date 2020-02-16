from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils import translation
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text

import re

from bootstrap_modal_forms.generic import BSModalLoginView

from utils.analysis import ProductAnalysis
from utils.decorators import group_required
from utils.tokens import account_activation_token
from .models import Post, UserProfile
from .forms import UserProfileForm, CustomAuthenticationForm, SignUpForm
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
            messages.warning(request, _('Warning: The research was not successful.'))
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
@group_required('admin')
def signup(request):
    context = {
        'title': 'Signup',
    }
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            password = User.objects.make_random_password()
            user = form.save(commit=False)
            user.set_password(password)
            user.is_active = False
            user.save()
            # user.groups.add(form.cleaned_data['groups'])
            UserProfile(user=user).save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your CSD Dashboard account.'
            message = render_to_string('dashboard/acc_active_email.html', {
                'user': user,
                'password': password,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, _('Success: Sign up succeeded. You can now Log in.'))
        context['errors'] = form.errors.items()
    else:
        form = SignUpForm()
    context['form'] = form
    return render(request, 'registration/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        messages.success(request, _('Thank you for your email confirmation. Now you can login your account.'))
        # context = {'title': _('Thank you for your email confirmation. Now you can login your account.')}
        return redirect('password_change')
    else:
        context = {'title': _('Activation link is invalid!')}
    return render(request, 'dashboard/done.html', context)


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
    template_name = 'dashboard/modal_form/login.html'
    success_message = _('Success: You were successfully logged in.')
    success_url = reverse_lazy('charts')


class CustomLogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/modal_form/logout.html'
