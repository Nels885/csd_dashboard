from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('charts/', views.charts, name='charts'),
    path('charts/ajax/', views.charts_ajax, name='charts_ajax'),
    path('late-prod/', views.late_products, name='late_prod'),
    path('autotronik/', views.autotronik, name='autotronik'),
    path('set_language/<str:user_language>/', views.set_language, name="set_lang"),
    path('profile/', views.user_profile, name="user_profile"),
    path('activity_log/', views.activity_log, name="activity_log"),
    path('search/', views.search, name="search"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('post/create/', views.PostCreateView.as_view(), name='create_post'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('weblink/create/', views.WebLinkCreateView.as_view(), name='create_weblink'),
    path('weblink/<int:pk>/update/', views.WebLinkUpdateView.as_view(), name='update_weblink'),
    path('weblink/<int:pk>/delete/', views.WebLinkDeleteView.as_view(), name='delete_weblink'),
    path('weblink/parts-suppliers/', views.supplier_links, name='supplier_links'),
    path('weblink/other/', views.other_links, name='other_links')
]
