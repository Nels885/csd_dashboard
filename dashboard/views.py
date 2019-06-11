from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.utils import translation

from squalaetp.models import Xelon
from .models import Post


def index(request):
    """
    View of index page
    :param request:
        Parameters of the request
    :return:
        Index page
    """
    posts = Post.objects.all()
    products = [
        ["RT6/RNEG2", "text-primary"],
        ["SMEG", "text-success"],
        ["RNEG", "text-danger"],
        ["NG4", "text-secondary"],
        ["DISPLAY", "text-dark"],
        ["RTx", "text-info"],
        ["AUTRES", "text-warning"]
    ]
    pending_prods = Xelon.objects.filter(type_de_cloture="").count()
    context = {
        'title': _("Dashboard"),
        'products': products,
        'pend_prods': pending_prods,
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
