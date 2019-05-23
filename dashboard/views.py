from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from squalaetp.models import Xelon


def index(request):
    products = [
        ["RT6/RNEG2", "text-primary"],
        ["SMEG", "text-success"],
        ["RT4", "text-info"],
        ["DISPLAY", "text-dark"],
        ["RNEG", "text-danger"],
        ["NG4", "text-secondary"]
    ]
    prod_nb = []
    for prod in products:
        prod_nb.append(Xelon.objects.filter(modele_produit__contains=prod[0]).count())

    context = {
        'title': 'Dashboard',
        'products': products,
        'prod_nb': prod_nb,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def logout(request):
    pass


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
    return render(request, 'dashboard/border.html', context)


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


def error(request):
    context = {
        'title': '404 Page',
    }
    return render(request, '404.html', context)


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
