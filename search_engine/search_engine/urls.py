"""
URL configuration for search_engine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from search.views import search_index, search_detail, search_advance
from login.views import login, user_manage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login),
    path('login',login),
    path('user', user_manage),
    path('index',search_index),
    path('search/', search_detail), 
    path('search/advance', search_advance), 
]
