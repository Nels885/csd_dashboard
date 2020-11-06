from django.shortcuts import render

from dashboard.models import WebLink

context = {
    'title': 'Info VAG'
}


def useful_links(request):
    web_links = WebLink.objects.filter(type='VAG')
    context.update(locals())
    return render(request, 'vag/useful_links.html', context)
