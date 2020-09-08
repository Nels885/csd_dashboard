from django.shortcuts import render

from dashboard.models import WebLink

context = {
    'title': 'Info FORD'
}


def useful_links(request):
    web_links = WebLink.objects.filter(type="FORD")
    context.update(locals())
    return render(request, 'ford/useful_links.html', context)


def tools(request):
    return render(request, 'ford/tools.html', context)
