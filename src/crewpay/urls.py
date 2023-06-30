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
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user/create/", views.create_user, name="create_user"),
    path("sync", views.sync_employees_view, name="sync"),
    path("payroll", views.run_payroll_view, name="payroll"),
    path("api/v1/", include("api.v1.urls")),
]
