from django.urls import path

from . import views

app_name = "manage"

urlpatterns = [
    path("", views.manage_index, name="manage_index"),
    path("stop_stream/<int:submission_id>", views.stop_stream, name="stop_stream"),
    path("retry_verification/<int:report_id>", views.retry_verification, name="retry_verification"),
]
