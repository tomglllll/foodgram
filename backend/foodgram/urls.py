from django.contrib import admin
from django.urls import include, path

from .views import redirect_short_link

urlpatterns = [
    path('s/<str:slug>/', redirect_short_link, name='redirect_short_link'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
