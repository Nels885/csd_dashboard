from django.utils.http import urlencode
from django.urls import reverse as original_reverse
from django.urls import reverse_lazy as original_reverse_lazy


def reverse(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = original_reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


def reverse_lazy(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = original_reverse_lazy(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


def http_referer(request):
    return request.META.get('HTTP_REFERER', reverse_lazy('index'))
