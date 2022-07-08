import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext as _
from django.utils import translation
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse, Http404

from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text

from bootstrap_modal_forms.generic import BSModalLoginView, BSModalUpdateView, BSModalDeleteView, BSModalCreateView

from utils.data.analysis import ProductAnalysis, IndicatorAnalysis, ToolsAnalysis
from utils.django.tokens import account_activation_token
from utils.django.urls import reverse, reverse_lazy, http_referer
from utils.django.validators import vin_psa_isvalid
from squalaetp.models import Xelon, Indicator, Sivin
from squalaetp.tasks import save_sivin_to_models
# from tools.models import EtudeProject
from psa.models import Corvet
from psa.tasks import save_corvet_to_models
from .models import Post, UserProfile, WebLink
from .forms import (
    UserProfileForm, CustomAuthenticationForm, SignUpForm, PostForm, ParaErrorList, WebLinkForm, ShowCollapseForm,
    SearchForm
)
from .tasks import cmd_sendemail_task


def index(request):
    """ View of index page """
    title = _("Home")
    posts = Post.objects.all().order_by('-timestamp')[:5]
    return render(request, 'dashboard/index.html', locals())


def charts(request):
    """ View of charts page """
    title = _("Dashboard")
    prods = ProductAnalysis()
    # projects = EtudeProject.objects.all()
    return render(request, 'dashboard/charts.html', locals())


def charts_ajax(request):
    """
    API endpoint that allows chart data to be viewed
    """
    prod = Indicator.count_prods()
    data = {"prodLabels": list(prod.keys()), "prodDefault": list(prod.values())}
    data.update(**IndicatorAnalysis().new_result(), **ToolsAnalysis().all())
    return JsonResponse(data)


def send_email_async(request):
    if request.user.is_staff:
        task = cmd_sendemail_task.delay("--late_products", "--pending_products", "--vin_error", "--vin_corvet")
        return JsonResponse({"task_id": task.id})
    raise Http404


@login_required
def products(request):
    """ View of products page """
    select_tab = request.GET.get('filter', 'late')
    template = 'dashboard/products/activity.html'
    prods = ProductAnalysis()
    context = {'title': _("Late Products"), 'select_tab': select_tab}
    if select_tab == 'pending':
        context = {'title': _("Pending Products"), 'select_tab': select_tab}
        context.update(prods.pending_products())
    elif select_tab == 'tronik':
        context = {'title': "Autotronik", 'select_tab': select_tab}
        context.update(prods.autotronik())
    else:
        context.update(prods.late_products())
    return render(request, template, context)


@login_required
def admin_products(request):
    """ View of Autotronik page """
    context = {'title': _("Admin Products"), 'select_tab': 'admin'}
    prods = ProductAnalysis()
    context.update(prods.admin_products())
    return render(request, 'dashboard/products/list.html', context)


@login_required
def vip_products(request):
    """ View of Autotronik page """
    context = {'title': _("VIP Products"), 'select_tab': 'vip'}
    prods = ProductAnalysis()
    context.update(prods.vip_products())
    return render(request, 'dashboard/products/list.html', context)


@login_required
def search(request):
    """ View of search page """
    query = request.GET.get('query')
    select = request.GET.get('select')
    if query and select:
        if Sivin.search(query):
            query = Sivin.search(query).first().codif_vin
        if query and select == 'atelier':
            files = Xelon.search(query)
            if files:
                messages.success(request, _(f'Success: The reseach for {query} was successful.'))
                if len(files) > 1:
                    return redirect(reverse('squalaetp:xelon', get={'filter': query}))
                return redirect('squalaetp:detail', pk=files.first().pk)
        elif query and select == 'sivin':
            sivins = Sivin.search(query)
            if sivins:
                return redirect('squalaetp:sivin_detail', immat=sivins.first().immat_siv)
        corvets = Corvet.search(query)
        if corvets:
            messages.success(request, _(f'Success: The reseach for {query} was successful.'))
            if len(corvets) > 1:
                return redirect(reverse('psa:corvet', get={'filter': query}))
            return redirect('psa:corvet_detail', vin=corvets.first().vin)
    messages.warning(request, _('Warning: The research was not successful.'))
    return redirect(http_referer(request))


def search_ajax(request):
    form = SearchForm(request.POST or None)
    data = {'url': reverse('dashboard:search'), 'task_id': None}
    if request.POST and form.is_valid():
        query = form.cleaned_data['query']
        select = form.cleaned_data['select']
        if query and select:
            if vin_psa_isvalid(query.upper()):
                if not Corvet.search(query):
                    task = save_corvet_to_models.delay(query)
                    data['task_id'] = task.id
            elif not re.match(r'^[9a-zA-Z]\d{9}$', str(query)) and (6 < len(query) < 11):
                if not Sivin.search(query):
                    task = save_sivin_to_models.delay(query)
                    data['task_id'] = task.id
            data['url'] = reverse('dashboard:search', get={'query': query, 'select': select})
    return JsonResponse(data)


def set_language(request, user_language):
    """
    View of language change
    :param user_language:
        Choice of the user's language
    """
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect(http_referer(request))


@login_required
def activity_log(request):
    """ View of activity log page """
    title = _("Dashboard")
    table_title = _('Activity log')
    logs = LogEntry.objects.filter(user_id=request.user.id)
    return render(request, 'dashboard/activity_log.html', locals())


@login_required
def user_profile(request):
    """ View of User profile page """
    title = _("User Profile")
    profil = get_object_or_404(UserProfile, user=request.user.id)
    if request.method == "POST":
        if "btn_avatar" in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=profil, error_class=ParaErrorList)
            if form.is_valid():
                form.save()
                messages.success(request, _('Success: Update profile picture!'))
        elif "btn_collapse":
            form = ShowCollapseForm(request.POST, instance=request.user.showcollapse, error_class=ParaErrorList)
            if form.is_valid():
                form.save()
                messages.success(request, _('Success: Update display configuration!'))
        errors = form.errors.items()
    form = UserProfileForm(error_class=ParaErrorList)
    form_show = ShowCollapseForm(instance=request.user.showcollapse, error_class=ParaErrorList)
    return render(request, 'dashboard/profile.html', locals())


@permission_required('auth.add_user', login_url='login')
def signup(request):
    """ View of Sign Up page """
    title = _("SignUp")
    card_title = _('Create an Account!')
    form = SignUpForm(request.POST or None)
    if request.POST and form.is_valid():
        password = User.objects.make_random_password()
        user = form.save(commit=False)
        user.set_password(password)
        user.is_active = False
        form.save()
        if form.cleaned_data['group']:
            for group in form.cleaned_data['group']:
                user.groups.add(group)
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
    errors = form.errors.items()
    return render(request, 'dashboard/register_form.html', locals())


def activate(request, uidb64, token):
    """ view for user activation by token """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, _('Thank you for your email confirmation. Now you can login your account.'))
        return redirect('password_change')
    else:
        context = {'title': _('Activation link is invalid!')}
    return render(request, 'dashboard/done.html', context)


class CustomLoginView(BSModalLoginView):
    """ View of modal login """
    authentication_form = CustomAuthenticationForm
    template_name = 'dashboard/modal/login.html'
    success_message = _('Success: You are logged in.')
    success_url = reverse_lazy('charts')


class CustomLogoutView(LoginRequiredMixin, TemplateView):
    """ View of modal logout """
    template_name = 'dashboard/modal/logout.html'


class PostCreateView(PermissionRequiredMixin, BSModalCreateView):
    """ View of modal post create """
    permission_required = 'dashboard.add_post'
    template_name = 'dashboard/modal/post_create.html'
    form_class = PostForm
    success_message = _('Success: Post was created.')
    success_url = reverse_lazy('index')


class PostUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    """ View of modal post update """
    model = Post
    permission_required = 'dashboard.change_post'
    template_name = 'dashboard/modal/post_update.html'
    form_class = PostForm
    success_message = _('Success: Post was updated.')
    success_url = reverse_lazy('index')


class PostDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    """ View of modal post delete """
    model = Post
    permission_required = 'dashboard.delete_post'
    template_name = 'dashboard/modal/post_delete.html'
    success_message = _('Success: Post was deleted.')
    success_url = reverse_lazy('index')


class WebLinkCreateView(PermissionRequiredMixin, BSModalCreateView):
    form_class = WebLinkForm
    permission_required = 'dashboard.add_weblink'
    template_name = 'dashboard/modal/weblink_create.html'
    success_message = _('Success: Web link was created')

    def get_success_url(self):
        return http_referer(self.request)


class WebLinkUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = WebLink
    form_class = WebLinkForm
    permission_required = 'dashboard.change_weblink'
    template_name = 'dashboard/modal/weblink_update.html'
    success_message = _('Success: Web link was updated')

    def get_success_url(self):
        return http_referer(self.request)


class WebLinkDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    """ View of modal post delete """
    model = WebLink
    permission_required = 'dashboard.delete_weblink'
    template_name = 'dashboard/modal/weblink_delete.html'
    success_message = _('Success: Web link was deleted.')

    def get_success_url(self):
        return http_referer(self.request)


@login_required
def supplier_links(request):
    title = "CSD Atelier"
    card_title = "Liens fournisseurs de pièces détachées"
    web_links = WebLink.objects.filter(type="PARTS_SUPPLIERS")
    return render(request, 'dashboard/weblink.html', locals())


@login_required
def other_links(request):
    title = "CSD Atelier"
    card_title = "Autres liens"
    web_links = WebLink.objects.filter(type="AUTRES")
    return render(request, 'dashboard/weblink.html', locals())
