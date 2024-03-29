"""vehicle_genius_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.redirect_to_vehicles, name='redirect_to_vehicles'),
    path('vehicles/', include('vehicles.urls', namespace='vehicles')),
    path('admin/', admin.site.urls),
    # override logout view to delete extra cookies
    path('accounts/logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth/', include('oauth.urls', namespace='oauth')),
    path('__reload__/', include('django_browser_reload.urls')),
]
