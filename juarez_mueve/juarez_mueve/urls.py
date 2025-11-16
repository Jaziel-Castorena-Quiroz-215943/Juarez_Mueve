from django.contrib import admin
from django.urls import path, include
from juarez_mueve.views import index, login_view, signup


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    
    path('login/', login_view, name='login'), 
    path('signup/', signup, name='signup'),
    
    path('transporte/', include('transporte.urls')),
    path('accounts/', include('allauth.urls')), 
    path('panel/', include('panel.urls')),
    
    path('panel/', include('panel.urls')),
]