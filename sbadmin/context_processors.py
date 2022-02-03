from django.contrib.auth.models import User
from _version import __version__

from constance import config


def get_release(request):
    return {'release': __version__}


def get_ip(request):
    return {'ip': request.META['REMOTE_ADDR']}


def get_wiki_url(request):
    return {'wiki_url': config.WIKI_URL}


def get_admin_emails(request):
    email_list = ",".join([values[0] for values in User.objects.filter(is_superuser=True).values_list('email')])
    return {'admin_emails': email_list}
