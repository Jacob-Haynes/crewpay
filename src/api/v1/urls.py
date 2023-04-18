from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from api.v1 import views
from api.v1.crewplanner.employees import employees_get
from api.v1.crewplanner.report import report_get
from api.v1.staffology.employees import sync_employees
from api.v1.staffology.employers import employers_get

urlpatterns = [
    path("", views.root),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("crewplanner/employees/", employees_get),
    path("crewplanner/report/", report_get),
    path("staffology/employers/", employers_get),
    path("staffology/employees/", sync_employees),
]
