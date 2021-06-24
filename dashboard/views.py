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
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.db.models import Q
from django.http import JsonResponse

from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text

from bootstrap_modal_forms.generic import BSModalLoginView, BSModalUpdateView, BSModalDeleteView, BSModalCreateView

from utils.data.analysis import ProductAnalysis, IndicatorAnalysis, ToolsAnalysis
from utils.django.tokens import account_activation_token
from squalaetp.models import Xelon, Indicator
from tools.models import EtudeProject
from psa.models import Corvet
from .models import Post, UserProfile, WebLink
from .forms import (
    UserProfileForm, CustomAuthenticationForm, SignUpForm, PostForm, ParaErrorList, WebLinkForm, ShowCollapseForm
)


def index(request):
    """ View of index page """
    title = _("Home")
    posts = Post.objects.all().order_by('-timestamp')[:5]
    return render(request, 'dashboard/index.html', locals())


def charts(request):
    """ View of charts page """
    title = _("Dashboard")
    prods = ProductAnalysis()
    projects = EtudeProject.objects.all()
    return render(request, 'dashboard/charts.html', locals())


def charts_ajax(request):
    """
    API endpoint that allows chart data to be viewed
    """
    indicator = IndicatorAnalysis()
    prod = Indicator.count_prods()
    tools = ToolsAnalysis()
    data = {"prodLabels": list(prod.keys()), "prodDefault": list(prod.values())}
    data.update(indicator.new_result())
    data.update(tools.suptech())
    data.update(tools.bga_time())
    data.update(tools.thermal_chamber_measure())
    return JsonResponse(data)


@login_required
def late_products(request):
    """ View of Late products page """
    context = {'title': _("Late Products"), 'select_tab': 'late'}
    prods = ProductAnalysis()
    context.update(prods.late_products())
    return render(request, 'dashboard/late_products/late_products.html', context)


@login_required
def autotronik(request):
    """ View of Autotronik page """
    context = {'title': _("Late Products"), 'select_tab': 'tronik'}
    prods = ProductAnalysis()
    context.update(prods.late_products())
    return render(request, 'dashboard/late_products/autotronik.html', context)


@login_required
def search(request):
    """ View of search page """
    query = request.GET.get('query')
    if query:
        query = query.upper().strip()
        # select = request.GET.get('select')
        files = Xelon.objects.filter(Q(numero_de_dossier=query) |
                                     Q(vin=query) |
                                     Q(corvet__electronique_44l__contains=query) |
                                     Q(corvet__electronique_44x__contains=query) |
                                     Q(corvet__electronique_44a__contains=query))
        if files and len(files) > 1:
            title = _('Search')
            table_title = _('Xelon files')
            return render(request, 'squalaetp/xelon_table.html', locals())
        elif files:
            return redirect('squalaetp:detail', pk=files.first().pk)
        else:
            corvets = Corvet.objects.filter(vin=query)
            if corvets:
                return redirect('psa:corvet_detail', vin=corvets.first().vin)
        messages.warning(request, _('Warning: The research was not successful.'))
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


@staff_member_required(login_url='login')
def signup(request):
    """ View of Sign Up page """
    title = _("SignUp")
    form = SignUpForm(request.POST or None)
    if request.POST and form.is_valid():
        password = User.objects.make_random_password()
        user = form.save(commit=False)
        user.set_password(password)
        user.is_active = False
        form.save()
        if form.cleaned_data['group']:
            user.groups.add(form.cleaned_data['group'])
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
    return render(request, 'dashboard/register.html', locals())


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
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class WebLinkUpdateView(PermissionRequiredMixin, BSModalUpdateView):
    model = WebLink
    form_class = WebLinkForm
    permission_required = 'dashboard.change_weblink'
    template_name = 'dashboard/modal/weblink_update.html'
    success_message = _('Success: Web link was updated')

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


class WebLinkDeleteView(PermissionRequiredMixin, BSModalDeleteView):
    """ View of modal post delete """
    model = WebLink
    permission_required = 'dashboard.delete_weblink'
    template_name = 'dashboard/modal/weblink_delete.html'
    success_message = _('Success: Web link was deleted.')

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        else:
            return reverse_lazy('index')


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
