from django.urls import include, path

from .v1.urls import v1_patterns

app_name = "api"

urlpatterns = [path("v1/", include(v1_patterns))]
