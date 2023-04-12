from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from api.v1 import views
from api.v1.crewplanner.employees import employees_get

urlpatterns = [
    path("", views.root),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("/crewplanner/employees/<str:stub>", employees_get),
]
