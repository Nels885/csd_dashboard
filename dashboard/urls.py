from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('set_language/<str:user_language>/', views.set_language, name="set-lang"),
    path('soft/', views.soft_list, name="soft-list"),
    path('soft/add/', views.soft_add, name="soft-add"),
    path('soft/<int:soft_id>/edit/', views.soft_edit, name="soft-edit"),
    path('buttons/', views.buttons, name='buttons'),
    path('cards/', views.cards, name='cards'),
    path('colors/', views.colors, name='colors'),
    path('border/', views.border, name='border'),
    path('animation/', views.animation, name='animation'),
    path('other/', views.other, name='other'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('password/', views.forgot_pwd, name='password'),
    path('blank/', views.blank, name='blank'),
    path('err_404/', views.error_404, name='error-404'),
    path('err_502/', views.error_502, name='error-502'),
    path('charts/', views.charts, name='charts'),
    path('table/', views.tables, name='tables'),
]
