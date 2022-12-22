from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path("", include("rest_framework.urls", namespace="rest_framework")),
]
