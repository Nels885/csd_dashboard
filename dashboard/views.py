from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils import translation

from .utils import ProductAnalysis
from .models import Post, CsdSoftware, User
from .forms import SoftwareForm, ParaErrorList


def index(request):
    """
    View of index page
    :param request:
        Parameters of the request
    :return:
        Index page
    """
    posts = Post.objects.all().order_by('-timestamp')
    context = {
        'title': _("Dashboard"),
        'prods': ProductAnalysis(),
        'posts': posts
    }
    return render(request, 'dashboard/index.html', context)


def set_language(request, user_language):
    """
    View of language change
    :param request:
        Parameters of the request
    :param user_language:
        Choice of the user's language
    :return:
        Index page
    """
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect('index')


def soft_list(request):
    softs = CsdSoftware.objects.all()
    context = {
        'title': 'Software',
        'table_title': _('Software list'),
        'softs': softs,
    }
    return render(request, 'dashboard/soft_table.html', context)


@login_required
def soft_add(request):
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
def soft_edit(request, soft_id):
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


# Demo views not use for the project

def buttons(request):
    context = {
        'title': 'Buttons',
    }
    return render(request, 'demo/buttons.html', context)


def cards(request):
    context = {
        'title': 'Cards',
    }
    return render(request, 'demo/cards.html', context)


def colors(request):
    context = {
        'title': 'Color Utilities',
    }
    return render(request, 'demo/colors.html', context)


def border(request):
    context = {
        'title': 'Border Utilities',
    }
    return render(request, 'demo/border.html', context)


def animation(request):
    context = {
        'title': 'Animation Utilities',
    }
    return render(request, 'demo/animation.html', context)


def other(request):
    context = {
        'title': 'Other Utilities',
    }
    return render(request, 'demo/other.html', context)


def login(request):
    context = {
        'title': 'Login',
    }
    return render(request, 'demo/login.html', context)


def register(request):
    context = {
        'title': 'Register',
    }
    return render(request, 'demo/register.html', context)


def forgot_pwd(request):
    context = {
        'title': 'Forgot Password',
    }
    return render(request, 'demo/forgot-password.html', context)


def blank(request):
    context = {
        'title': 'Blank Page',
    }
    return render(request, 'demo/blank.html', context)


def error_404(request):
    context = {
        'title': '404 Page',
    }
    return render(request, '404.html', context)


def error_502(request):
    context = {
        'title': '502 Page',
    }
    return render(request, '502.html', context)


def charts(request):
    context = {
        'title': 'Charts',
    }
    return render(request, 'demo/charts.html', context)


def tables(request):
    context = {
        'title': 'Tables',
    }
    return render(request, 'demo/tables.html', context)
