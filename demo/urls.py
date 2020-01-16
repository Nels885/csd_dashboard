from django.urls import path

from . import views

app_name = 'demo'

urlpatterns = [
    path('buttons/', views.buttons, name='buttons'),
    path('cards/', views.cards, name='cards'),
    path('colors/', views.colors, name='colors'),
    path('border/', views.border, name='border'),
    path('animation/', views.animation, name='animation'),
    path('other/', views.other, name='other'),
    path('login/', views.login, name='login'),
    path('password/', views.forgot_pwd, name='password'),
    path('register/', views.register, name='register'),
    path('blank/', views.blank, name='blank'),
    path('err_404/', views.error_404, name='error-404'),
    path('err_500/', views.error_500, name='error-500'),
    path('charts/', views.charts, name='charts'),
    path('table/', views.tables, name='tables'),
]
