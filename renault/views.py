from django.shortcuts import render

from dashboard.models import WebLink

context = {
    'title': 'Info Renault'
}


def useful_links(request):
    web_links = WebLink.objects.filter(type='RENAULT')
    context.update(locals())
    return render(request, 'renault/useful_links.html', context)
