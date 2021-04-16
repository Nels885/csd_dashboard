from django.shortcuts import render
from django.http import JsonResponse

from .utils import derive_precode
from dashboard.models import WebLink

context = {
    'title': 'Info Renault'
}


def useful_links(request):
    web_links = WebLink.objects.filter(type='RENAULT')
    context.update(locals())
    return render(request, 'renault/useful_links.html', context)


def tools(request):
    return render(request, 'renault/tools.html', context)


def ajax_decode(request):
    precode = request.GET.get('precode')
    data = derive_precode(precode)
    return JsonResponse(data)
