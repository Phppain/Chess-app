from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import GameViewSet, UserViewSet

router = DefaultRouter()
router.register(r'Game', GameViewSet)  
router.register(r'User', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
    # path('api/chess/new-game/', GameViewSet.start_new, name='start_new'),
    # path('api/chess/get-users/', UserViewSet.get_users, name='get_users')
]