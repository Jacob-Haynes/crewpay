from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from api.v1 import views

urlpatterns = [
    path("", views.root, name="root"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
