"""sbadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from dashboard.views import index
from .views import get_progress_view, download_file_view

favicon_view = RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))


def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero


urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('celery-progress/', get_progress_view, name='progress'),
    path('download-file/', download_file_view, name="download"),
    path('favicon.ico', favicon_view),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('raspeedi/', include('raspeedi.urls')),
    path('squalaetp/', include('squalaetp.urls')),
    path('reman/', include('reman.urls')),
    path('tools/', include('tools.urls')),
    path('import-export/', include('import_export.urls')),
    path('psa/', include('psa.urls')),
    path('ford/', include('ford.urls')),
    path('renault/', include('renault.urls')),
    path('vag/', include('vag.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', index, name="index"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
