from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'prog', views.ProgViewSet, basename='prog')
router.register(r'cal', views.CalViewSet, basename='cal')
router.register(r'xelon', views.XelonViewSet, basename='xelon')
router.register(r'corvet', views.CorvetViewSet, basename='corvet')
router.register(r'unlock', views.UnlockViewSet, basename='unlock')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('charts/', views.charts, name="charts"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='token_auth'),
    path('temp/', views.thermal_temp, name='temp'),
    path('doc/', views.documentation, name='doc')
]
