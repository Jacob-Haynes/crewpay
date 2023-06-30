from django.urls import include, path

from api.v1 import views
from api.v1.crewplanner.endpoints import employees_get, report_get


urlpatterns = [
    path("", views.root),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("crewplanner/employees/", employees_get),
    path("crewplanner/report/", report_get),
]
