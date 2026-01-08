"""
URL configuration for digital_responsibility project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.shortcuts import render
from django.http import HttpResponse

def home_view(request):
   return HttpResponse("<h1>CyberHunk API</h1><p>Status: Running</p>", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('social_auth.urls')),
    path('insights/', include('insights.urls')),
    path('', home_view, name='home'), 
]
