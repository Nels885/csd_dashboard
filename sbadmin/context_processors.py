from django.contrib.auth.models import User
from _version import __version__

from constance import config

from dashboard.forms import SearchForm


def global_infos(request):
    return {
        'release': __version__, 'ip': request.META['REMOTE_ADDR'],
        'website_domain': config.WEBSITE_DOMAIN, 'wiki_url': config.WIKI_URL
    }


def global_emails(request):
    email_list = ",".join([values[0] for values in User.objects.filter(is_superuser=True).values_list('email')])
    return {'admin_emails': email_list}


def global_forms(request):
    return {
        'search_form': SearchForm()
    }
