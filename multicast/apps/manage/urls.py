from django.urls import path

from . import views

app_name = "manage"

urlpatterns = [
    path("", views.manage_index, name="manage_index"),
    path("stop_stream/<int:submission_id>", views.stop_stream, name="stop_stream"),
    path("remove_stream/<int:submission_id>", views.remove_stream, name="remove_stream"),
    path("edit_stream/<int:submission_id>", views.edit_stream, name="edit_stream"),
    path("retry_verification/<int:report_id>", views.retry_verification, name="retry_verification"),
]
