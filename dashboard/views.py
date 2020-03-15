from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.utils import translation
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

from bootstrap_modal_forms.generic import BSModalLoginView, BSModalUpdateView, BSModalDeleteView, BSModalCreateView

from utils.data.analysis import ProductAnalysis
from utils.django.tokens import account_activation_token
from .models import Post, UserProfile
from .forms import UserProfileForm, CustomAuthenticationForm, SignUpForm, PostForm
from squalaetp.models import Xelon


def index(request):
    """
    View of index page
    """
    posts = Post.objects.all().order_by('-timestamp')[:5]
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


@login_required
def late_products(request):
    prods = ProductAnalysis()
    prods = prods.pendingQueries.filter(delai_au_en_jours_calendaires__gt=3, type_de_cloture='')[:100]
    context = {
        'title': _("Late Products"),
        'prods': prods
    }
    return render(request, 'dashboard/late_products.html', context)


@login_required
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
            messages.success(request, _('Success: Modification done!'))
        context['errors'] = form.errors.items()
    else:
        form = UserProfileForm()
    context['form'] = form
    return render(request, 'registration/profile.html', context)


@login_required
@staff_member_required(login_url='login')
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
            if form.cleaned_data['group']:
                user.groups.add(form.cleaned_data['group'])
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
        return redirect('password_change')
    else:
        context = {'title': _('Activation link is invalid!')}
    return render(request, 'dashboard/done.html', context)


@login_required
@staff_member_required(login_url='login')
def config_edit(request):

    if request.method == 'POST':
        query = request.POST.get('config')
        with open(settings.CONF_FILE, 'w+') as file:
            file.write(query)
        messages.success(request, _('Success: Modification done!'))

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


class CustomLoginView(BSModalLoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'dashboard/modal/login.html'
    success_message = _('Success: You are logged in.')
    success_url = reverse_lazy('charts')


class CustomLogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/modal/logout.html'


class PostCreateView(PermissionRequiredMixin, BSModalCreateView):
    permission_required = 'dashboard.add_post'
    template_name = 'dashboard/modal/post_create.html'
    form_class = PostForm
    success_message = _('Success: Post was created.')
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'test'
        return context


class PostUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = Post
    permission_required = 'dashboard.change_post'
    template_name = 'dashboard/modal/post_update.html'
    form_class = PostForm
    success_message = _('Success: Post was updated.')
    success_url = reverse_lazy('index')


class PostDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    model = Post
    permission_required = 'dashboard.delete_post'
    template_name = 'dashboard/modal/post_delete.html'
    success_message = _('Success: Post was deleted.')
    success_url = reverse_lazy('index')
