from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('xelon/', views.xelon_table, name='xelon'),
    path('corvet/', views.corvet_table, name='corvet')
]
