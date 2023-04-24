"""
URL configuration for crewpay project.

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
from django.urls import include, path

from crewpay import views

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", views.root, name="root"),
    path("onboard", views.onboard, name="onboard"),
    path("settings", views.settings, name="settings"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("token", views.token, name="token"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("api/v1/", include("api.v1.urls")),
    path("user/create/", views.create_user, name="create_user"),
    path("user/connect/staffology", views.create_staffology_user),
]
