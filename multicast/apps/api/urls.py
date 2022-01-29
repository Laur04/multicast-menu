from django.urls import path

from .views import *


urlpatterns = [
    path("add/", SubmissionAdd.as_view(), name="api_add"),
    path("remove/", SubmissionRemove.as_view(), name="api_remove"),
]
